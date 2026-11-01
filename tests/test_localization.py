import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from image_refs import markdown_images,transform_markdown,source_inventory,output_inventory
import localize_images as tool

PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aNaQAAAAASUVORK5CYII=')

class ReferenceTests(unittest.TestCase):
    def test_reference_html_srcset_and_code_protection(self):
        text='![one][ref]\n\n[ref]: https://old.example/a.png\n\n<img src="https://old.example/b.png" srcset="https://old.example/c.png 2x">\n\n    ![literal](https://old.example/code.png)\n\n`![inline](https://old.example/inline.png)`\n'
        self.assertEqual(markdown_images(text),{'https://old.example/a.png','https://old.example/b.png','https://old.example/c.png'})
        updated=transform_markdown(text,lambda s:s.replace('https://old.example/','/images/'))
        self.assertIn('https://old.example/code.png',updated)
        self.assertIn('https://old.example/inline.png',updated)
        self.assertIn('[ref]: /images/a.png',updated)
    def test_svg_validation_rejects_error_pages_and_external_dependencies(self):
        self.assertEqual(tool.extension(b'<svg xmlns="http://www.w3.org/2000/svg"><path fill="url(#g)"/></svg>'),'.svg')
        for data in [b'<html>Login</html>',b'<svg><image href="https://remote.example/p.png"/></svg>']:
            with self.assertRaises(ValueError):tool.extension(data)

class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'site';self.root.mkdir()
        self.sources=[Path(self.tmp.name)/'original',Path(self.tmp.name)/'drafts']
        for p in self.sources:p.mkdir()
        for name in ['reports','content/post/1','data','static/images/recovered']:(self.root/name).mkdir(parents=True)
        (self.root/'hugo.toml').write_text("baseURL = 'https://example.org/'\n")
        self.article=self.root/'content/post/1/index.md'
    def write(self,url):
        self.article.write_text(json.dumps({'title':'文章','image':url},ensure_ascii=False)+'\n\n![图]('+url+')\n\n`![代码]('+url+')`\n\n[普通链接](https://docs.example/guide)\n')
    def apply(self,**kwargs):
        with contextlib.redirect_stdout(io.StringIO()):return tool.migrate(self.root,self.sources,**kwargs)
    def test_unicode_mapping_dedupe_and_repeatability(self):
        url='https://old.example/中文/a.png';self.write(url)
        (self.sources[0]/'a.png').write_bytes(PNG)
        self.assertTrue(self.apply())
        report=json.loads((self.root/'reports/image-localization.json').read_text())
        row=report['images'][0]
        self.assertEqual(row['sha256'],hashlib.sha256(PNG).hexdigest())
        self.assertEqual((self.root/'static'/row['url'].lstrip('/')).read_bytes(),PNG)
        self.assertIn('`![代码]('+url+')`',self.article.read_text())
        self.assertIn('[普通链接](https://docs.example/guide)',self.article.read_text())
        before=self.article.read_bytes()
        self.assertTrue(self.apply())
        self.assertEqual(self.article.read_bytes(),before)
        self.assertEqual(len(json.loads((self.root/'reports/image-localization.json').read_text())['images']),1)
        self.assertEqual(tool.checks(self.root),[])
    def test_original_gitea_branch_wins_over_different_draft_file(self):
        self.write('https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/a.png')
        (self.sources[0]/'a.png').write_bytes(PNG)
        (self.sources[1]/'a.png').write_bytes(PNG+b'draft')
        self.assertTrue(self.apply())
        row=json.loads((self.root/'reports/image-localization.json').read_text())['images'][0]
        self.assertEqual(row['sha256'],hashlib.sha256(PNG).hexdigest())
        self.assertEqual(row['source_kind'],'original-image-repository-blog-branch')
    def test_unresolved_does_not_rewrite_any_content(self):
        self.write('https://old.example/a.png');before=self.article.read_bytes()
        (self.sources[0]/'a.png').write_bytes(PNG)
        (self.sources[1]/'a.png').write_bytes(PNG+b'different')
        self.assertFalse(self.apply())
        self.assertEqual(self.article.read_bytes(),before)
        self.assertFalse(list((self.root/'static/images/recovered').glob('*')))
    def test_cached_image_without_extension_uses_verified_bytes(self):
        url='https://note.example/api/123?method=download';self.write(url)
        export=Path(self.tmp.name)/'export';(export/'files').mkdir(parents=True)
        (export/'files/blob').write_bytes(PNG)
        (export/'index.html').write_text(json.dumps([{'url':url,'file':'/files/blob','sha256':hashlib.sha256(PNG).hexdigest()}]))
        self.assertTrue(self.apply(cache_export=export))
        row=json.loads((self.root/'reports/image-localization.json').read_text())['images'][0]
        self.assertTrue(row['url'].endswith('.png'))
    def test_output_scans_feeds_json_and_css_without_matching_code_examples(self):
        public=self.root/'public';public.mkdir()
        (public/'index.html').write_text('<img src="/images/a.png"><pre><code>&lt;img src="https://code.example/a.png"&gt;</code></pre>')
        (public/'index.xml').write_text('<rss><description>&lt;img src="https://remote.example/feed.png"&gt;</description></rss>')
        (public/'search.json').write_text(json.dumps([{'image':'https://remote.example/cover.png','content':'literal <img src="https://code.example/x.png">'}]))
        (public/'style.css').write_text('.cover{background:url(https://remote.example/bg.png)}')
        urls=output_inventory(public)
        self.assertEqual(set(urls),{'/images/a.png','https://remote.example/feed.png','https://remote.example/cover.png','https://remote.example/bg.png'})

if __name__=='__main__':unittest.main()
