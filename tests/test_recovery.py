import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import recover_images

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aNaQAAAAASUVORK5CYII=')
URL = 'https://old.example/screenshot.png'

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'site'
        self.drafts = Path(self.temp.name)/'drafts'
        self.drafts.mkdir()
        (self.root/'reports').mkdir(parents=True)
        self.article = self.root/'content/post/1/index.md'
        self.article.parent.mkdir(parents=True)
        self.article.write_text(json.dumps({'title':'公开文章','image':URL})+'\n\n![截图]('+URL+')\n```text\n'+URL+'\n```\n')
        (self.root/'reports/migration.json').write_text(json.dumps({'items':[{'cid':1,'path':'content/post/1/index.md'}]}))
        (self.root/'reports/resources.json').write_text(json.dumps({'fetch_warnings':[{'url':URL,'cids':[1]}]}))
        self.patcher=patch.object(recover_images,'ROOT',self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
    def run_recovery(self):
        with contextlib.redirect_stdout(io.StringIO()):
            recover_images.recover(self.drafts)
        return json.loads((self.root/'reports/image-recovery.json').read_text())
    def test_restores_original_bytes_preserves_code_and_is_repeatable(self):
        (self.drafts/'screenshot.png').write_bytes(PNG)
        r=self.run_recovery()
        row=r['recovered'][0]
        self.assertEqual((self.root/'static'/row['url'].lstrip('/')).read_bytes(),PNG)
        self.assertEqual(row['sha256'],hashlib.sha256(PNG).hexdigest())
        self.assertIn('```text\n'+URL+'\n```',self.article.read_text())
        self.assertIn(row['url'],self.article.read_text())
        original=self.article.read_bytes()
        # A subsequent build's resource report must not erase the recovery audit.
        (self.root/'reports/resources.json').write_text('{"fetch_warnings":[]}')
        self.assertEqual(self.run_recovery(),r)
        self.assertEqual(self.article.read_bytes(),original)
    def test_encoded_report_matches_unicode_source_url(self):
        raw = 'https://old.example/中文/screenshot.png'
        encoded = 'https://old.example/%E4%B8%AD%E6%96%87/screenshot.png'
        self.article.write_text(json.dumps({'title':'公开文章'})+'\n\n![截图]('+raw+')\n')
        (self.root/'reports/resources.json').write_text(json.dumps({'fetch_warnings':[{'url':encoded,'cids':[1]}]}))
        (self.drafts/'screenshot.png').write_bytes(PNG)
        r=self.run_recovery()
        self.assertIn(r['recovered'][0]['url'],self.article.read_text())
        self.assertNotIn(raw,self.article.read_text())

    def test_does_not_guess_ambiguous_files(self):
        for name,data in [('a',PNG),('b',PNG+b'different')]:
            p=self.drafts/name/'screenshot.png';p.parent.mkdir();p.write_bytes(data)
        r=self.run_recovery()
        self.assertEqual(r['recovered'],[])
        self.assertEqual(r['unresolved'][0]['reason'],'ambiguous-local-files')
        self.assertIn(URL,self.article.read_text())

if __name__=='__main__':
    unittest.main()
