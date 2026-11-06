import unittest
from bench.suites import load_suite, grade
class SuiteTests(unittest.TestCase):
 def test_custom_counts(self):
  tasks=load_suite('custom')
  self.assertEqual(len(tasks),19)
  self.assertEqual(sum(t['kind']=='code' for t in tasks),9)
 def test_public(self): self.assertEqual(len(load_suite('humaneval')),164)
 def test_agent_wrong(self):
  task=next(t for t in load_suite('custom') if t['id']=='agent_units')
  self.assertFalse(grade(task,{'content':'{}'})['functional_pass'])
 def test_agent_good(self):
  task=next(t for t in load_suite('custom') if t['id']=='agent_units')
  self.assertTrue(grade(task,{'content':'{"energy_wh":300,"average_w":450,"autonomy_hours":4}'})['strict_pass'])
if __name__=='__main__':unittest.main()

class GradingRegressionTests(unittest.TestCase):
 def test_early_exit_never_passes(self):
  for task in [load_suite('custom')[0],load_suite('humaneval')[0]]:
   self.assertFalse(grade(task,{'content':'print("BENCH_TESTS_COMPLETED"); raise SystemExit(0)'})['functional_pass'])
 def test_candidate_cannot_override_equality(self):
  task=load_suite('custom')[0]
  self.assertFalse(grade(task,{'content':'def eq(a,b): return True\ndef merge_intervals(intervals): return None'})['functional_pass'])
 def test_future_import_allowed(self):
  task=load_suite('humaneval')[0];r=task['source']
  self.assertTrue(grade(task,{'content':'from __future__ import annotations\n'+r['prompt']+r['canonical_solution']})['functional_pass'])

class AgentShapeTests(unittest.TestCase):
 def test_scalar_json_is_failure(self):
  task=next(t for t in load_suite('custom') if t['id']=='agent_units')
  for text in ['null','1','true','[]']:
   self.assertFalse(grade(task,{'content':text})['functional_pass'])
 def test_missing_reason_is_not_strict(self):
  task=next(t for t in load_suite('custom') if t['id']=='agent_refuse_write')
  self.assertFalse(grade(task,{'content':'{"action_performed":false}'})['strict_pass'])

class UnknownTaskTests(unittest.TestCase):
 def test_unknown_agent_task_is_not_pass(self):
  from bench.agent_grading import agent_score
  self.assertFalse(agent_score('not_defined',{'content':'{}'})['functional_pass'])
