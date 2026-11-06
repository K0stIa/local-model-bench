import pathlib,tempfile,unittest
from bench.metadata import source_digest
class MetadataTests(unittest.TestCase):
 def test_digest_tracks_sources_not_results(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'bench').mkdir();(p/'results').mkdir()
   (p/'bench/a.py').write_text('x=1');a=source_digest(p)
   (p/'results/a.json').write_text('{}');self.assertEqual(a,source_digest(p))
   (p/'bench/a.py').write_text('x=2');self.assertNotEqual(a,source_digest(p))
