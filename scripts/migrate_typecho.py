#!/usr/bin/env python3
"""Read-only Typecho migration. No comments, private content or remote assets are fetched."""
import argparse
from datetime import datetime
import html
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DB = 'typecho_offical'
ELIGIBLE = "c.type='post' AND c.status='publish' AND COALESCE(c.password,'')=''"
SELECTED = f"(({ELIGIBLE}) OR (c.type='page' AND c.status='publish' AND COALESCE(c.password,'')='' AND c.slug IN ('project','links')))"
OLD = 'https://blog.fjy8018.top'

def query(sql):
    env = os.environ.copy()
    env['MYSQL_PWD'] = env['WARP_PASSWORD']
    result = subprocess.run([env.get('MYSQL_BIN', '/opt/homebrew/opt/mysql-client/bin/mysql'),
        '-u', 'codex#mysql-prod', '--host', 'gate.fjy8018.top', '--port', '33306',
        '--ssl-mode=REQUIRED', '--connect-timeout=10', '--enable-cleartext-plugin',
        '--batch', '--raw', '--skip-column-names', '--default-character-set=utf8mb4',
        '--execute', sql], env=env, check=True, capture_output=True, text=True)
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]

def extract():
    # JSON encoding preserves real newlines and literal backslashes without mysql TSV escaping.
    # One mysql process / connection for the entire export; never retry failed authentication.
    statements = {
        'contents': f"SELECT JSON_OBJECT('cid',c.cid,'title',c.title,'slug',c.slug,'type',c.type,'created',c.created,'modified',c.modified,'text',c.text) FROM {DB}.typecho_contents c WHERE {SELECTED} ORDER BY c.cid",
        'fields': f"SELECT JSON_OBJECT('cid',f.cid,'name',f.name,'value',CASE f.type WHEN 'int' THEN CAST(f.int_value AS CHAR) WHEN 'float' THEN CAST(f.float_value AS CHAR) ELSE f.str_value END) FROM {DB}.typecho_fields f JOIN {DB}.typecho_contents c ON f.cid=c.cid WHERE {SELECTED}",
        'metas': f"SELECT JSON_OBJECT('cid',r.cid,'name',m.name,'slug',m.slug,'type',m.type) FROM {DB}.typecho_relationships r JOIN {DB}.typecho_metas m ON m.mid=r.mid JOIN {DB}.typecho_contents c ON c.cid=r.cid WHERE {SELECTED}",
        'links': f"SELECT JSON_OBJECT('name',name,'url',url,'image',image,'description',description) FROM {DB}.typecho_links ORDER BY `order`,lid",
    }
    sql = ';\n'.join(
        f"SELECT JSON_OBJECT('_collection','{name}');\n{statement}"
        for name, statement in statements.items()
    ) + ';'
    data = {name: [] for name in statements}
    collection = None
    for row in query(sql):
        if '_collection' in row:
            collection = row['_collection']
        else:
            data[collection].append(row)
    return data

def absolute(url):
    if url.startswith(('data:', '#', 'mailto:', 'tel:')):
        return url
    return urljoin(OLD + '/', url)

def outside_code(text, transform):
    # Fenced and inline code are deliberately left byte-for-byte unchanged.
    parts = re.split(r'(```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~|`+[^`\n]+`+)', text, flags=re.S)
    return ''.join(part if i % 2 else transform(part) for i, part in enumerate(parts))

def migrate(data):
    posts = [c for c in data['contents'] if c['type'] == 'post']
    targets = {str(c['cid']): f"/archives/{c['cid']}/" if c['type']=='post' else f"/{c['slug']}.html" for c in data['contents']}
    fields = {}
    tax = {}
    for f in data['fields']:
        fields.setdefault(f['cid'], {})[f['name']] = f['value']
    for m in data['metas']:
        tax.setdefault(m['cid'], {}).setdefault(m['type'], []).append(m['name'])
    report = {'source': DB, 'posts': len(posts), 'pages': sum(c['type'] == 'page' for c in data['contents']), 'items': [], 'unresolved_post_references': [], 'legacy_syntax': [], 'remote_resources': []}
    expected_paths = set()
    def article_link(url):
        # Markdown permits angle-bracketed destinations; normalize before URL resolution.
        if url.startswith('<') and url.endswith('>'):
            url = url[1:-1]
        full = urlsplit(absolute(html.unescape(url)))
        if full.netloc.lower() != urlsplit(OLD).netloc:
            return url
        path = re.sub(r'^/index\.php(?=/)', '', full.path)
        match = re.fullmatch(r'/archives/(\d+)/?', path)
        if match and match[1] in targets:
            return targets[match[1]] + (('?' + full.query) if full.query else '') + (('#'+full.fragment) if full.fragment else '')
        if path in ('/project.html','/links.html'):
            return path
        return absolute(url) if not url.startswith(('#','http://','https://','mailto:','tel:','data:')) else url
    for c in data['contents']:
        cid = c['cid']
        f = fields.get(cid, {})
        resources = set()
        def resource(url):
            value = absolute(url)
            if value.startswith(('http://', 'https://')):
                resources.add(value)
            return value
        def transform(body):
            def post_ref(m):
                ref = m[1]
                if ref not in targets:
                    report['unresolved_post_references'].append({'cid': cid, 'target_cid': int(ref)})
                return f"[相关文章]({targets.get(ref, OLD + '/index.php/archives/' + ref + '/')})"
            body = re.sub(r'\[post\s+cid=[\"\x27]?(\d+)[\"\x27]?\s*/?\]', post_ref, body)
            def external_card(m):
                attrs = dict(re.findall(r'(\w+)="([^"\n]*)"', m[1]))
                url = attrs.get('url', '').replace('\\/', '/')
                if not url:
                    return m[0]
                title = attrs.get('title', url).replace('[', r'\[').replace(']', r'\]')
                result = f"[{title}]({article_link(url)})"
                if attrs.get('intro'):
                    result += ' — ' + attrs['intro']
                if attrs.get('cover'):
                    result += f"\n\n![{title}]({resource(attrs['cover'])})"
                return result
            body = re.sub(r'\[post\s+([^\]\n]+)\s*/\]', external_card, body)
            body = re.sub(r'\[scode[^\]\n]*\]', '\n<aside class="legacy-note">\n\n', body)
            body = body.replace('[/scode]', '\n\n</aside>\n')
            # Inline markdown images: preserve absolute URLs; complete relative origins.
            body = re.sub(r'(!\[[^\]]*\]\(<?)([^\s)>]+)', lambda m: m[1]+resource(m[2]), body)
            # Reference definitions may point at images or downloadable files. Preserve origins.
            body = re.sub(r'(?m)^(\s*\[[^\]]+\]:\s*<?)([^\s>]+)', lambda m: m[1]+(article_link(m[2]) if article_link(m[2]) != m[2] else resource(m[2])), body)
            body = re.sub(r'(<(?:img|source|video|audio)\b[^>]*?\b(?:src|poster)=[\"\x27])([^\"\x27]+)', lambda m: m[1]+resource(m[2]), body, flags=re.I)
            body = re.sub(r'(?<!!)\[([^\]]+)\]\(([^\s)]+)([^)]*)\)', lambda m: '['+m[1]+']('+article_link(m[2])+m[3]+')', body)
            body = re.sub(r'(<a\b[^>]*\bhref=[\"\x27])([^\"\x27]+)', lambda m: m[1]+article_link(m[2]), body, flags=re.I)
            return body
        body = (c['text'] or '').removeprefix('<!--markdown-->').replace('\r\n','\n')
        body = outside_code(body, transform).strip() + '\n'
        if c['slug'] == 'links' and c['type'] == 'page':
            body = '{{< friend-links >}}\n'
        metadata = dict(title=c['title'], date=datetime.fromtimestamp(c['created'],ZoneInfo('Asia/Shanghai')).isoformat(), lastmod=datetime.fromtimestamp(c['modified'],ZoneInfo('Asia/Shanghai')).isoformat(), typecho_cid=cid, url=targets[str(cid)], comments=False, draft=False)
        if c['type']=='post':
            metadata.update(slug=str(cid), categories=tax.get(cid,{}).get('category',[]), tags=tax.get(cid,{}).get('tag',[]))
            if f.get('customSummary'):
                metadata['description'] = f['customSummary']
            if f.get('thumb') and f['thumb'].strip():
                metadata['image'] = resource(f['thumb'].strip())
            metadata['math'] = str(f.get('mathjax','')).lower() not in ('','0','false','off','none')
            path = ROOT / 'content/post' / str(cid) / 'index.md'
        else:
            path = ROOT / 'content/page' / c['slug'] / 'index.md'
        expected_paths.add(path.resolve())
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n\n'+body)
        report['items'].append({'cid':cid,'path':str(path.relative_to(ROOT)),'url':targets[str(cid)]})
        legacy = ''.join(re.split(r'(```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~|`+[^`\n]+`+)', body, flags=re.S)[::2])
        tokens = re.findall(r'\[/?(?:post|scode|hide|collapse|tabs|tab|tip|note|warning|success|info|danger|button|video|audio|player|photos|album|hplayer|vplayer)(?:\s+[^\]\n]*)?\s*/?\]', legacy)
        report['legacy_syntax'].extend({'cid':cid,'syntax':t} for t in sorted(set(tokens)) if not re.fullmatch(r'\[(?:x|X|toc|TOC)\]',t))
        report['remote_resources'].extend({'cid':cid,'url':u} for u in sorted(resources))
    # Remove only stale files previously generated by this tool.
    manifest = ROOT/'reports/migration.json'
    if manifest.exists():
        for item in json.loads(manifest.read_text()).get('items',[]):
            path = (ROOT/item['path']).resolve()
            generated = re.fullmatch(r'content/(?:post/\d+|page/(?:project|links))/index\.md', item['path'])
            if generated and path not in expected_paths and path.is_relative_to((ROOT/'content').resolve()):
                path.unlink(missing_ok=True)
    (ROOT/'data').mkdir(exist_ok=True)
    friends = [{**link, 'image': absolute(link['image']) if link.get('image') else ''} for link in data['links']]
    (ROOT/'data/friends.json').write_text(json.dumps(friends,ensure_ascii=False,indent=2)+'\n')
    manifest.parent.mkdir(exist_ok=True)
    manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'posts':len(posts),'pages':sum(c['type']=='page' for c in data['contents']),'unresolved_post_references':len(report['unresolved_post_references']),'syntax_candidates':len(report['legacy_syntax']),'remote_resources':len(report['remote_resources'])}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract',action='store_true',help='Read fresh eligible content into ignored local snapshot')
    args=parser.parse_args()
    snapshot=ROOT/'.migration/public-content.json'
    if args.extract:
        data=extract()
        snapshot.parent.mkdir(exist_ok=True)
        snapshot.write_text(json.dumps(data,ensure_ascii=False))
    else:
        data=json.loads(snapshot.read_text())
    migrate(data)

if __name__=='__main__':
    main()
