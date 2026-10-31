#!/usr/bin/env python3
"""Validate rendered output without reading the database or fetching remote resources."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://fjiayang.github.io'

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.scripts = []
        self.comments = False
        self.canonical = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('a', 'link') and attrs.get('href'):
            self.urls.append(attrs['href'])
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs['src'])
        if attrs.get('id') in ('disqus_thread', 'comments', 'giscus') or any(c in attrs.get('class', '').split() for c in ('article-comments','giscus','utterances','twikoo')):
            self.comments = True
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href'))

def main():
    public = ROOT / 'public'
    manifest = json.loads((ROOT/'reports/migration.json').read_text())
    errors = []
    expected = {item['cid'] for item in manifest['items'] if item['path'].startswith('content/post/')}
    actual = set()
    for p in (ROOT/'content/post').glob('*/index.md'):
        if not p.read_text().lstrip().startswith('{'):
            continue
        metadata, _ = json.JSONDecoder().raw_decode(p.read_text())
        if metadata.get('typecho_cid') is None:
            continue
        actual.add(metadata['typecho_cid'])
        if metadata.get('comments') is not False or metadata.get('draft') is not False:
            errors.append(f'Unexpected publication flags: {p.relative_to(ROOT)}')
    if expected != actual or len(actual) != manifest['posts']:
        errors.append('Article manifest and content differ')
    for url in ['/', '/archives/', '/categories/', '/tags/', '/search/', '/search/index.json', '/project.html', '/links.html', '/404.html', '/index.xml', '/sitemap.xml', '/robots.txt', '/images/avatar.png'] + [item['url'] for item in manifest['items']]:
        p = public/url.lstrip('/')
        if url.endswith('/'):
            p = p/'index.html'
        if not p.is_file():
            errors.append(f'Missing output: {url}')
    for p in public.rglob('*.html'):
        document = Document()
        document.feed(p.read_text())
        if document.comments:
            errors.append(f'Comment component: {p.relative_to(public)}')
        for script in document.scripts:
            if re.search(r'disqus|giscus|utteranc|gitalk|twikoo|waline|remark42|cactus.chat', script, re.I):
                errors.append(f'Comment script: {script}')
        for url in document.urls:
            parsed = urlsplit(url)
            if parsed.scheme not in ('', 'https', 'http') or (parsed.netloc and parsed.netloc != urlsplit(BASE).netloc):
                continue
            if not parsed.path.startswith('/'):
                continue
            path = public / unquote(parsed.path).lstrip('/')
            if parsed.path.endswith('/'):
                path = path/'index.html'
            if not path.is_file() and not (path/'index.html').is_file():
                errors.append(f'{p.relative_to(public)} -> missing {url}')
    search = json.loads((public/'search/index.json').read_text())
    # Search template indexes articles only; independent pages must not leak other content.
    search_urls = {entry['permalink'].removeprefix(BASE) for entry in search}
    article_urls = {item['url'] for item in manifest['items'] if item['cid'] in expected}
    if not article_urls.issubset(search_urls):
        errors.append('Search index omits migrated public articles')
    if manifest['legacy_syntax']:
        errors.append('Unconverted theme syntax remains')
    errors = sorted(set(errors))
    if errors:
        print('\n'.join(errors[:50]))
        print(f'{len(errors)} validation errors')
        sys.exit(1)
    print(f'Validated {len(actual)} public articles, navigation, internal links, search index, feeds and absence of comments.')

if __name__ == '__main__':
    main()
