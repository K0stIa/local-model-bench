import unittest
from bench.aggregate_comparison import summarize,distribution
class AggregateTests(unittest.TestCase):
 def test_no_raw_export(self):
  r={'task':'code_test','wall_s':1,'request':{'secret':'PRIVATE'},'response':{'content':'PRIVATE'},'score':{'functional_pass':True,'strict_pass':False}}
  s=summarize([r]);self.assertNotIn('PRIVATE',str(s));self.assertEqual(s['coding']['functional'],1);self.assertEqual(s['coding']['strict'],0)
 def test_duplicates_rejected(self):
  with self.assertRaises(ValueError):summarize([{'task':'code_test'}]*2)
 def test_finite(self):self.assertEqual(distribution([None,float('nan'),2,4])['median'],3)
