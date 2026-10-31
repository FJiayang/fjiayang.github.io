import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import migrate_typecho as migration


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.patch = patch.object(migration, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def convert(self, body, cid=1):
        data = {'contents': [dict(cid=cid, title='中文标题', slug=str(cid), type='post', created=1700000000, modified=1700000001, text=body)], 'fields': [], 'metas': [], 'links': []}
        with contextlib.redirect_stdout(io.StringIO()):
            migration.migrate(data)
        return (self.root/f'content/post/{cid}/index.md').read_text()

    def test_code_and_literal_newlines_are_preserved(self):
        code = '```sh\nprintf "hello\\n"\n[post cid="99" /]\n```'
        result = self.convert('<!--markdown-->正文\r\n\n' + code + '\n`[post cid="99" /]`')
        self.assertIn(code, result)
        self.assertIn('`[post cid="99" /]`', result)
        self.assertNotIn('<!--markdown-->', result)
        self.assertIn('+08:00', result)

    def test_images_attachments_and_article_links(self):
        result = self.convert('![图](https://images.example/a.png)\n![图](/usr/uploads/b.png)\n[附件](/usr/uploads/a.zip)\n[自己](https://blog.fjy8018.top/index.php/archives/1/#test)\n[私密引用](https://blog.fjy8018.top/archives/99/)')
        self.assertIn('![图](https://images.example/a.png)', result)
        self.assertIn('![图](https://blog.fjy8018.top/usr/uploads/b.png)', result)
        self.assertIn('[附件](https://blog.fjy8018.top/usr/uploads/a.zip)', result)
        self.assertIn('[自己](/archives/1/#test)', result)
        self.assertIn('[私密引用](https://blog.fjy8018.top/archives/99/)', result)

    def test_old_shortcodes_and_unavailable_post(self):
        result = self.convert('[post cid="1" /]\n[post cid="99" /]\n[post url="https:\\/\\/example.com/" title="参考" cover="https://example.com/a.png" /]\n[scode type="yellow"]提示[/scode]')
        self.assertIn('[相关文章](/archives/1/)', result)
        self.assertIn('https://blog.fjy8018.top/index.php/archives/99/', result)
        self.assertIn('[参考](https://example.com/)', result)
        self.assertIn('https://example.com/a.png', result)
        self.assertIn('<aside', result)
        self.assertNotIn('[scode', result)
        report = json.loads((self.root/'reports/migration.json').read_text())
        self.assertEqual(report['unresolved_post_references'], [{'cid':1,'target_cid':99}])
        self.assertEqual(report['legacy_syntax'], [])

    def test_regeneration_removes_only_previously_generated_content(self):
        first = self.convert('公开文章', 1)
        manual = self.root/'content/post/manual/index.md'
        manual.parent.mkdir()
        manual.write_text('手写文章')
        self.convert('另一篇文章', 2)
        self.assertFalse((self.root/'content/post/1/index.md').exists())
        self.assertTrue(manual.exists())
        again = self.convert('另一篇文章', 2)
        self.assertEqual(again, (self.root/'content/post/2/index.md').read_text())

    def test_extraction_excludes_nonpublic_content_and_comments(self):
        statements = []
        def fake_query(sql):
            statements.append(sql)
            return [{'_collection': 'contents'}, {'cid': 1}, {'_collection': 'links'}, {'name': 'friend'}]
        with patch.object(migration, 'query', fake_query):
            data = migration.extract()
        self.assertEqual(data['contents'], [{'cid': 1}])
        self.assertEqual(data['links'], [{'name': 'friend'}])
        self.assertEqual(len(statements), 1)
        self.assertNotIn('typecho_comments', '\n'.join(statements))
        for sql in statements[:3]:
            self.assertIn("c.status='publish'", sql)
            self.assertIn("COALESCE(c.password,'')=''", sql)
            self.assertIn("c.type='post'", sql)

if __name__ == '__main__':
    unittest.main()
