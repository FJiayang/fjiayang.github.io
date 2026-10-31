"""Build small offline Hugo fixtures to verify Stack cover fallback behavior."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
HUGO=os.environ.get('HUGO_BIN') or shutil.which('hugo')

@unittest.skipUnless(HUGO, 'Hugo Extended is required for template integration tests')
class CoverTests(unittest.TestCase):
    def test_cover_priority_and_rendered_body_images(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture=Path(directory)
            shutil.copytree(ROOT/'layouts',fixture/'layouts')
            shutil.copy(ROOT/'go.mod',fixture/'go.mod')
            shutil.copy(ROOT/'go.sum',fixture/'go.sum')
            (fixture/'static').mkdir()
            for name in ['explicit.png','body.png','reference.png','html.png']:
                shutil.copy(ROOT/'static/images/avatar.png',fixture/'static'/name)
            (fixture/'hugo.toml').write_text('''baseURL = 'https://example.org/'
defaultContentLanguage = 'zh'
[module]
  [[module.imports]]
    path = 'github.com/CaiJimmy/hugo-theme-stack/v4'
[params.comments]
  enabled = false
  provider = ''
[params.imageProcessing.content]
  enabled = false
[params.imageProcessing.thumbnail]
  enabled = false
[markup.goldmark.renderer]
  unsafe = true
''')
            cases={
                'explicit': ('image: /explicit.png\n', '![正文](/body.png)', '/explicit.png'),
                'inline': ('', '```md\n![代码示例](/code.png)\n```\n\n![正文](/body.png)', '/body.png'),
                'reference': ('', '![引用][image]\n\n[image]: /reference.png', '/reference.png'),
                'html': ('', '<img src="/html.png" alt="HTML 图片">', '/html.png'),
                'none': ('', '只有正文，没有图片。', None),
            }
            for slug,(extra,body,_) in cases.items():
                p=fixture/'content/post'/slug/'index.md';p.parent.mkdir(parents=True)
                p.write_text(f'---\ntitle: {slug}\ndate: 2020-01-01\nurl: /archives/{slug}/\n{extra}---\n\n{body}\n')
            result=subprocess.run([HUGO,'--source',str(fixture),'--quiet'],capture_output=True,text=True,env={**os.environ,'GOPROXY':'off','GOSUMDB':'off'})
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            for slug,(_,_,expected) in cases.items():
                output=(fixture/f'public/archives/{slug}/index.html').read_text()
                cover=re.search(r'<div class="article-image">(.*?)</div>',output,re.S)
                if expected:
                    self.assertIsNotNone(cover,slug)
                    self.assertIn(f'src="{expected}"',cover[1],slug)
                else:
                    self.assertIsNone(cover,slug)
            home=(fixture/'public/index.html').read_text()
            self.assertEqual(home.count('class="article-image"'),4)

if __name__=='__main__':
    unittest.main()
