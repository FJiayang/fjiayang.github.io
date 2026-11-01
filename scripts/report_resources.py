#!/usr/bin/env python3
"""Summarize Stack's remote-image fetch warnings without downloading resources again."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote
import tomllib
from image_refs import source_inventory,remote

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    args=parser.parse_args()
    warnings={}
    for line in args.log.read_text().splitlines():
        match=re.search(r'(?:Failed to fetch remote resource|Unable to get remote resource) "([^"]+)"',line)
        if match:
            reason='timeout' if 'deadline exceeded' in line else ('403 Forbidden' if 'Forbidden' in line else ('404 Not Found' if 'Not Found' in line else 'fetch failed'))
            warnings[match[1]]=reason
    inventory=json.loads((ROOT/'reports/migration.json').read_text())
    report={'method':'Stack v4.0.3 default image helper during Hugo build; failures are non-blocking; no independent availability probe',
            'listed_resource_urls':sum(remote(u,tomllib.loads((ROOT/'hugo.toml').read_text())['baseURL']) for u in source_inventory(ROOT)),
            'fetch_warnings':[]}
    for url,reason in sorted(warnings.items()):
        cids=sorted({x['cid'] for x in inventory['remote_resources'] if unquote(x['url'])==unquote(url)})
        report['fetch_warnings'].append(dict(url=url,reason=reason,cids=cids))
    (ROOT/'reports/resources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"Recorded {len(warnings)} remote fetch warnings. Image URLs were retained.")

if __name__=='__main__':
    main()
