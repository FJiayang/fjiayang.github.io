#!/usr/bin/env python3
"""Recover only reported broken images from local draft assets; no network or database access."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

from migrate_typecho import outside_code

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

def image_type(path):
    with path.open('rb') as stream:
        signature = stream.read(16)
    if signature.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if signature.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if signature.startswith((b'GIF87a', b'GIF89a')):
        return '.gif'
    if signature.startswith(b'RIFF') and signature[8:12] == b'WEBP':
        return '.webp'
    raise ValueError(f'Not a supported raster image: {path.name}')

def recover(draft_root):
    draft_root = draft_root.resolve()
    index = defaultdict(list)
    for path in draft_root.rglob('*'):
        if path.is_file() and path.suffix.lower() in EXTENSIONS and path.resolve().is_relative_to(draft_root):
            index[path.name.casefold()].append(path)
    manifest = json.loads((ROOT/'reports/migration.json').read_text())
    articles = {row['cid']: ROOT/row['path'] for row in manifest['items']}
    baseline = json.loads((ROOT/'reports/resources.json').read_text())
    report_path = ROOT/'reports/image-recovery.json'
    previous = {}
    if report_path.exists():
        saved = json.loads(report_path.read_text())
        previous = {row['original_url']: row for row in saved['recovered']}
        # Preserve the original recovery scope even if a later build refreshes resources.json.
        baseline['fetch_warnings'] = [
            {'url': row['original_url'], 'cids': [a['cid'] for a in row['articles']]}
            for row in saved['recovered'] + saved['unresolved']
        ]
    drafts = [(path, path.read_text()) for path in draft_root.rglob('*.md') if path.resolve().is_relative_to(draft_root)]
    recovered, unresolved = [], []
    replacements = defaultdict(dict)
    for warning in sorted(baseline['fetch_warnings'], key=lambda row: row['url']):
        url = warning['url']
        name = Path(unquote(urlsplit(url).path)).name
        if url in previous:
            # Already verified copies do not depend on the original source directory.
            old = previous[url]
            destination = ROOT/'static'/old['url'].lstrip('/')
            if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest() != old['sha256']:
                raise ValueError(f'Previously recovered image missing or modified: {old["url"]}')
            recovered.append(old)
            for cid in warning['cids']:
                replacements[cid][url] = old['url']
            continue
        candidates = list(index.get(name.casefold(), []))
        method = 'exact-filename'
        if not candidates and urlsplit(url).hostname == 'img.zcool.cn' and '@' in name:
            # Zcool appends a rendition instruction; the supplied original keeps its .jpg name.
            candidates = list(index.get(name.split('@', 1)[0].casefold(), []))
            method = 'original-filename-without-cdn-transform'
        if not candidates:
            method = 'published-image-alt-filename'
            for cid in warning['cids']:
                text = articles[cid].read_text()
                for match in re.finditer(r'!\[([^\]]+)\]\('+re.escape(url)+r'(?:\s|\))', text):
                    candidates.extend(index.get(match[1].casefold(), []))
        # Duplicate filenames are only acceptable if their bytes are identical.
        by_hash = {hashlib.sha256(path.read_bytes()).hexdigest(): path for path in sorted(set(candidates))}
        titles = []
        for cid in warning['cids']:
            metadata, _ = json.JSONDecoder().raw_decode(articles[cid].read_text())
            titles.append({'cid': cid, 'title': metadata['title']})
        if len(by_hash) != 1:
            unresolved.append({'original_url': url, 'articles': titles, 'reason': 'no-local-file' if not by_hash else 'ambiguous-local-files'})
            continue
        digest, source = next(iter(by_hash.items()))
        extension = image_type(source)
        destination = ROOT/'static/images/recovered'/f'{digest[:20]}{extension}'
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(source, destination)
        if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
            raise ValueError('Recovered destination checksum mismatch')
        target_url = '/images/recovered/'+destination.name
        matching_drafts = [str(path.relative_to(draft_root)) for path, text in drafts if name in text or source.name in text]
        recovered.append({'original_url': url, 'url': target_url, 'source': str(source.relative_to(draft_root)), 'source_directory': draft_root.name, 'drafts': matching_drafts, 'match_method': method, 'sha256': digest, 'bytes': source.stat().st_size, 'articles': titles})
        for cid in warning['cids']:
            replacements[cid][url] = target_url
    for cid, mapping in replacements.items():
        path = articles[cid]
        text = path.read_text()
        metadata, end = json.JSONDecoder().raw_decode(text)
        if metadata.get('image') in mapping:
            metadata['image'] = mapping[metadata['image']]
        def transform(body):
            for old, new in mapping.items():
                for variant in {old, unquote(old)}:
                    body = body.replace(variant, new)
            return body
        body = outside_code(text[end:], transform)
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+body)
    report = {'baseline_failed_urls': len(baseline['fetch_warnings']), 'recovered': recovered, 'unresolved': unresolved}
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f'Recovered {len(recovered)} unique URLs across {len(replacements)} articles; {len(unresolved)} URLs have no confirmed local replacement.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft_root', type=Path)
    args = parser.parse_args()
    recover(args.draft_root)
