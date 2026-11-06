import unittest
from bench.performance import body, metrics, snapshot, validate_profile
class PerformanceTests(unittest.TestCase):
    def test_fixed_budget(self):
        b=body('test',{'decode_tokens':128,'seed':42},False)
        self.assertFalse(b['cache_prompt']);self.assertTrue(b['ignore_eos']);self.assertEqual(b['n_predict'],128)
    def test_missing_timings(self):
        with self.assertRaises(ValueError):metrics({})
    def test_negative_timings(self):
        with self.assertRaises(ValueError):metrics({'timings':{'prompt_n':-1}})
    def test_memory(self):self.assertGreater(snapshot()['system']['MemAvailable_kib'],0)
    def test_profile(self):
        with self.assertRaises(ValueError):validate_profile({'decode_tokens':True})
    def test_metrics(self):
        self.assertEqual(metrics({'timings':{'prompt_n':10,'prompt_ms':1,'predicted_n':128,'predicted_ms':100}})['predicted_n'],128)
