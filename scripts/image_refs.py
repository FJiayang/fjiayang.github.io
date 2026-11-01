"""Image-reference discovery shared by migration and offline build validation."""
import html
import json
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

from markdown_it import MarkdownIt

MARKDOWN = MarkdownIt("commonmark", {"html": True})

IMAGE_KEYS = {'image', 'images', 'avatar', 'favicon', 'thumbnail', 'poster', 'cover'}
CSS_URL = re.compile(r'url\(\s*[\"\x27]?([^\s)\"\x27]+)', re.I)
IMAGE_SUFFIXES = {'.png','.jpg','.jpeg','.gif','.webp','.svg','.ico','.bmp','.avif'}

def normalize(url):
    url = html.unescape(url.strip().strip('<>'))
    if url.startswith('//'):
        url = 'https:' + url
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), unquote(p.path), p.query, p.fragment))

def remote(url, base):
    p = urlsplit(normalize(url))
    return bool(p.netloc and p.hostname != urlsplit(base).hostname)

def srcset_urls(value):
    # Data URI commas belong to the URI; these images need no local files.
    if value.lstrip().startswith('data:'):
        return []
    return [part.strip().split()[0] for part in value.split(',') if part.strip()]

class ImageHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = set()
        self.code_depth = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('pre','code'):
            self.code_depth += 1
        if self.code_depth:
            return
        if tag in ('img','input') and (tag=='img' or a.get('type')=='image'):
            if a.get('src'): self.images.add(a['src'])
        if tag in ('img','source'):
            self.images.update(srcset_urls(a.get('srcset','')))
        if tag=='video' and a.get('poster'): self.images.add(a['poster'])
        if tag in ('image','use'):
            for key in ('href','xlink:href'):
                if a.get(key): self.images.add(a[key])
        if tag=='meta' and (a.get('property') in ('og:image','og:image:url','twitter:image') or a.get('name')=='twitter:image') and a.get('content'):
            self.images.add(a['content'])
        if tag=='link' and ('icon' in a.get('rel','') or (a.get('rel')=='preload' and a.get('as')=='image')) and a.get('href'):
            self.images.add(a['href'])
        self.images.update(CSS_URL.findall(a.get('style','')))
    def handle_endtag(self, tag):
        if tag in ('pre','code'):
            self.code_depth = max(0,self.code_depth-1)

def html_images(text):
    p=ImageHTML();p.feed(text)
    return p.images

def transform_markdown(text, transform):
    """Preserve CommonMark fenced/indented code and exact backtick code spans."""
    lines=text.splitlines(keepends=True)
    offsets=[0]
    for line in lines:offsets.append(offsets[-1]+len(line))
    protected=[]
    for token in MARKDOWN.parse(text):
        if token.type in ('fence','code_block') and token.map:
            protected.append((offsets[token.map[0]],offsets[token.map[1]]))
    def inline(chunk):
        parts=[];start=0;cursor=0
        while cursor<len(chunk):
            m=re.search(r'`+',chunk[cursor:])
            if not m:break
            opening=cursor+m.start();size=len(m[0])
            closing=re.search(r'(?<!`)`{'+str(size)+r'}(?!`)',chunk[opening+size:])
            if not closing:cursor=opening+size;continue
            end=opening+size+closing.end()
            parts.extend([transform(chunk[start:opening]),chunk[opening:end]])
            start=end;cursor=end
        parts.append(transform(chunk[start:]))
        return ''.join(parts)
    parts=[];start=0
    for a,b in sorted(protected):
        parts.extend([inline(text[start:a]),text[a:b]]);start=b
    parts.append(inline(text[start:]))
    return ''.join(parts)

def markdown_images(text):
    found=set()
    def walk(tokens):
        for token in tokens:
            if token.type=='image':found.add(token.attrGet('src'))
            elif token.type in ('html_inline','html_block'):found.update(html_images(token.content))
            if token.children:walk(token.children)
    walk(MARKDOWN.parse(text))
    return found

def json_images(data):
    result=set()
    if isinstance(data,dict):
        for key,value in data.items():
            if key.lower() in IMAGE_KEYS:
                if isinstance(value,str) and value:result.add(value)
                elif isinstance(value,list):result.update(v for v in value if isinstance(v,str) and v)
            if isinstance(value,(dict,list)):result.update(json_images(value))
    elif isinstance(data,list):
        for value in data:result.update(json_images(value))
    return result

def source_inventory(root):
    found={}
    def add(path, urls):
        for url in urls:
            if url and not url.startswith(('#','data:')):
                found.setdefault(normalize(url),set()).add(str(path.relative_to(root)))
    for path in (root/'content').rglob('*.md'):
        text=path.read_text()
        if text.lstrip().startswith('{'):
            meta,end=json.JSONDecoder().raw_decode(text)
            add(path,json_images(meta));text=text[end:]
        else:
            # YAML/TOML front matter image values are checked without rewriting their format.
            for m in re.finditer(r'(?m)^\s*(?:image|avatar|favicon|cover):\s*[\"\x27]?([^\s\"\x27]+)',text):add(path,[m[1]])
        add(path,markdown_images(text))
    for path in (root/'data').rglob('*.json'):
        add(path,json_images(json.loads(path.read_text())))
    import tomllib
    for path in root.glob('*.toml'):
        add(path,json_images(tomllib.loads(path.read_text())))
    for folder in ('assets','static','layouts'):
        for path in (root/folder).rglob('*'):
            if path.suffix.lower() in ('.css','.scss'):
                add(path,CSS_URL.findall(path.read_text()))
            elif path.suffix.lower() in ('.html','.svg'):
                add(path,html_images(path.read_text()))
    return found

def output_inventory(public):
    found={}
    def add(path,urls):
        for u in urls:
            if u and not u.startswith(('#','data:')):
                found.setdefault(normalize(u),set()).add(str(path.relative_to(public)))
    for path in public.rglob('*'):
        if not path.is_file():continue
        if path.suffix=='.html':add(path,html_images(path.read_text()))
        elif path.suffix=='.json':add(path,json_images(json.loads(path.read_text())))
        elif path.suffix in ('.css','.svg'):
            text=path.read_text();add(path,CSS_URL.findall(text))
            if path.suffix=='.svg':add(path,html_images(text))
        elif path.suffix=='.xml':
            # RSS content is escaped HTML; parse XML first, then its HTML fragments.
            tree=ET.fromstring(path.read_bytes())
            for node in tree.iter():
                if node.text and '<' in node.text:add(path,html_images(node.text))
    return found
