#!/usr/bin/env python3
"""One-time full image migration and permanent source/output validation. No database access."""
import argparse
from collections import defaultdict
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import urllib.request
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree as ET

from image_refs import source_inventory,output_inventory,normalize,remote,IMAGE_SUFFIXES,transform_markdown

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCES=[Path('/Users/fjy/Documents/workspace/images/img'),Path('/Users/fjy/Documents/workspace/images/images'),Path('/Users/fjy/Documents/workspace/blog-note/01博客')]

def digest(data):return hashlib.sha256(data).hexdigest()

def extension(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):return '.png'
    if data.startswith(b'\xff\xd8\xff'):return '.jpg'
    if data.startswith((b'GIF87a',b'GIF89a')):return '.gif'
    if data.startswith(b'RIFF') and data[8:12]==b'WEBP':return '.webp'
    if data.startswith(b'\x00\x00\x01\x00'):return '.ico'
    if data.startswith(b'BM'):return '.bmp'
    if data[4:8]==b'ftyp' and any(x in data[8:40] for x in (b'avif',b'avis')):return '.avif'
    try:
        svg=ET.fromstring(data)
        if svg.tag.split('}')[-1]!='svg':raise ValueError('not SVG')
        for e in svg.iter():
            if e.tag.split('}')[-1] in ('image','use','script'):
                for key,value in e.attrib.items():
                    if key.endswith('href') and value and not value.startswith(('#','data:')):
                        raise ValueError('SVG contains external resource reference')
        for value in re.findall(rb'url\(\s*[\"\x27]?([^\s)\"\x27]+)',data):
            if not value.startswith((b'#',b'data:')):raise ValueError('SVG contains external CSS resource')
        return '.svg'
    except ET.ParseError:pass
    raise ValueError('Response is not a supported self-contained image')

def variants(url):
    decoded=normalize(url)
    p=urlsplit(decoded)
    encoded=p._replace(path=quote(p.path,safe='/@:+,;=-._~!$&\x27()*')).geturl()
    return {url,decoded,encoded,html.escape(url,quote=False),html.escape(encoded,quote=False)}

def rewrite(text,mapping):
    replacements={variant:target for url,target in mapping.items() for variant in variants(url)}
    if not replacements:return text
    pattern=re.compile('|'.join(re.escape(key) for key in sorted(replacements,key=len,reverse=True)))
    return pattern.sub(lambda m:replacements[m[0]],text)

def replace_json(value,mapping):
    if isinstance(value,dict):return {k:replace_json(v,mapping) for k,v in value.items()}
    if isinstance(value,list):return [replace_json(v,mapping) for v in value]
    if isinstance(value,str):return rewrite(value,mapping)
    return value

def checks(root,public=None):
    import tomllib
    base=tomllib.loads((root/'hugo.toml').read_text())['baseURL']
    inventory=output_inventory(public) if public else source_inventory(root)
    errors=[]
    for url,refs in inventory.items():
        if remote(url,base):errors.append(f'Remote image: {url} ({sorted(refs)[0]})')
        elif url.startswith('/') or urlsplit(url).hostname==urlsplit(base).hostname:
            path=(public or root/'static')/unquote(urlsplit(url).path).lstrip('/')
            if not path.is_file():errors.append(f'Missing local image: {url}')
    manifest=root/'reports/image-localization.json'
    if manifest.exists():
        report=json.loads(manifest.read_text())
        if report['unresolved']:errors.append('Full image migration has unresolved items')
        for row in report['images']:
            path=(public or root/'static')/row['url'].lstrip('/')
            if not path.is_file() or digest(path.read_bytes())!=row['sha256']:errors.append('Image checksum mismatch: '+row['url'])
    return sorted(set(errors))

def migrate(root,sources,cache_export=None,replacements=None,download=False):
    import tomllib
    base=tomllib.loads((root/'hugo.toml').read_text())['baseURL']
    inventory=source_inventory(root)
    index=defaultdict(list)
    for source in sources:
        for path in source.rglob('*'):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path.resolve().is_relative_to(source.resolve()):index[path.name.casefold()].append(path)
    exported={}
    if cache_export:
        for row in json.loads((cache_export/'index.html').read_text()):
            path=cache_export/row['file'].lstrip('/')
            if digest(path.read_bytes())!=row['sha256']:raise ValueError('Exported cache checksum mismatch')
            exported[normalize(row['url'])]=path
    existing={digest(path.read_bytes()):path for path in (root/'static/images/recovered').glob('*') if path.is_file()}
    staged=[];unresolved=[]
    replacements=replacements or {}
    remote_urls=sorted(u for u in inventory if remote(u,base))
    for url in remote_urls:
        path=None;kind=None
        if url in replacements:path=replacements[url];kind='approved-replacement'
        name=Path(unquote(urlsplit(url).path)).name
        candidates=index.get(name.casefold(),[])
        # Exact source path on the blog branch is authoritative for the old Gitea image repo.
        old_path=unquote(urlsplit(url).path)
        prefix='/fjy8018/images/raw/branch/blog/img/'
        if path is None and urlsplit(url).hostname=='gitea.fjy8018.top' and old_path.startswith(prefix):
            source=sources[0]/old_path.removeprefix(prefix)
            if source.is_file():path=source;kind='original-image-repository-blog-branch'
        if path is None and candidates:
            hashes={digest(p.read_bytes()):p for p in candidates}
            if len(hashes)==1:path=next(iter(hashes.values()));kind='exact-local-filename'
            else:unresolved.append({'original_url':url,'references':sorted(inventory[url]),'reason':'ambiguous-local-files'});continue
        if path is None and url in exported:path=exported[url];kind='one-time-hugo-resource-export'
        if path is None and download:
            try:
                req=urllib.request.Request(quote(url,safe=':/?=&%+@#;,-._~!$\x27()*'),headers={'User-Agent':'Mozilla/5.0 image-migration','Referer':base})
                with urllib.request.urlopen(req,timeout=20) as response:data=response.read(30*1024*1024+1)
                if len(data)>30*1024*1024:raise ValueError('Download exceeds 30 MiB')
                extension(data)
                staging=root/'.migration/image-downloads'/digest(data)
                staging.parent.mkdir(parents=True,exist_ok=True);staging.write_bytes(data)
                path=staging;kind='one-time-source-download'
            except Exception as error:unresolved.append({'original_url':url,'references':sorted(inventory[url]),'reason':str(error)});continue
        if path is None:unresolved.append({'original_url':url,'references':sorted(inventory[url]),'reason':'no-confirmed-local-image'});continue
        try:
            data=path.read_bytes();ext=extension(data);sha=digest(data)
        except ValueError as error:unresolved.append({'original_url':url,'references':sorted(inventory[url]),'reason':str(error)});continue
        target=existing.get(sha,root/'static/images/recovered'/f'{sha[:20]}{ext}')
        row={'original_url':url,'url':'/'+str(target.relative_to(root/'static')),'sha256':sha,'bytes':len(data),'source_kind':kind,'source_file':path.name,'references':sorted(inventory[url])}
        for source_root in sources:
            if path.resolve().is_relative_to(source_root.resolve()):
                row['source_directory']=str(Path(source_root.parent.name)/source_root.name)
                row['source_file']=str(path.relative_to(source_root))
                break
        staged.append((row,path,target))
        existing[sha]=target
    report={'complete':not unresolved,'external_urls_before':len(remote_urls),'images':[row for row,_,_ in staged],'unresolved':unresolved}
    report_path=root/'reports/image-localization.json'
    # On repeated runs retain the full audit while checking live references afresh.
    if report_path.exists():
        previous=json.loads(report_path.read_text())
        current={row['original_url']:row for row,_,_ in staged}
        for row in previous['images']:
            if normalize(row['original_url']) in inventory or row['url'] in inventory:
                current.setdefault(row['original_url'],row)
        report['images']=sorted(current.values(),key=lambda row:row['original_url'])
        if previous.get('complete'):
            report['external_urls_before']=max(previous['external_urls_before'],len(remote_urls))
    legacy=root/'reports/image-recovery.json'
    if legacy.exists():
        combined={row['original_url']:row for row in report['images']}
        for row in json.loads(legacy.read_text())['recovered']:
            if row['url'] not in inventory:continue
            combined.setdefault(normalize(row['original_url']),{
                'original_url':normalize(row['original_url']),'url':row['url'],
                'sha256':row['sha256'],'bytes':row['bytes'],'source_kind':'previously-recovered-original',
                'source_file':row['source'],'references':sorted(inventory[row['url']])})
        report['images']=sorted(combined.values(),key=lambda row:row['original_url'])
    report['recorded_original_urls']=len(report['images'])
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if unresolved:
        print(f'{len(unresolved)} unresolved image URLs; source files and published references were not changed.')
        return False
    mapping={row['original_url']:row['url'] for row,_,_ in staged}
    for row,source,target in staged:
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copyfile(source,target)
        if digest(target.read_bytes())!=row['sha256']:raise ValueError('Destination checksum mismatch')
    for folder in ('content','data','assets','layouts'):
        for path in (root/folder).rglob('*'):
            if not path.is_file() or path.suffix.lower() not in ('.md','.json','.html','.css','.scss','.svg'):continue
            text=path.read_text()
            if path.suffix=='.json':updated=json.dumps(replace_json(json.loads(text),mapping),ensure_ascii=False,indent=2)+'\n'
            elif path.suffix=='.md' and text.lstrip().startswith('{'):
                metadata,end=json.JSONDecoder().raw_decode(text)
                updated=json.dumps(replace_json(metadata,mapping),ensure_ascii=False,indent=2)+transform_markdown(text[end:],lambda chunk:rewrite(chunk,mapping))
            elif path.suffix=='.md':updated=transform_markdown(text,lambda chunk:rewrite(chunk,mapping))
            else:updated=rewrite(text,mapping)
            if updated!=text:path.write_text(updated)
    for path in root.glob('*.toml'):
        text=path.read_text();updated=rewrite(text,mapping)
        if updated!=text:path.write_text(updated)
    print(f'Localized {len(staged)} URL mappings; {len(existing)} deduplicated image files; no unresolved URLs.')
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['apply','check-source','check-output'])
    parser.add_argument('--source',action='append',type=Path)
    parser.add_argument('--cache-export',type=Path)
    parser.add_argument('--replacement',action='append',default=[],help='Explicitly approved ORIGINAL_URL=LOCAL_FILE')
    parser.add_argument('--download-missing',action='store_true')
    args=parser.parse_args()
    if args.mode=='apply':
        replacements={normalize(value.rsplit('=',1)[0]):Path(value.rsplit('=',1)[1]) for value in args.replacement}
        ok=migrate(ROOT,args.source or DEFAULT_SOURCES,args.cache_export,replacements,args.download_missing)
        if not ok:raise SystemExit(1)
    else:
        errors=checks(ROOT,ROOT/'public' if args.mode=='check-output' else None)
        if errors:
            print('\n'.join(errors[:50]));print(f'{len(errors)} image validation errors');raise SystemExit(1)
        print('All image references are local and all recorded checksums match.')

if __name__=='__main__':main()
