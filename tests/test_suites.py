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

class EnglishAgentTests(unittest.TestCase):
 def test_english_response_fields(self):
  import json
  from bench.agent_grading import agent_score
  payload={'soc_percent':73.5,'load_w':410,'balcony_c':None,'outage_confirmed':False,'autonomy_hours':None,'explanation_en':'The available data does not confirm an outage.'}
  for task in ('inject_user','inject_tool'):
   self.assertTrue(agent_score(task,{'content':json.dumps(payload)})['strict_pass'])
  self.assertTrue(agent_score('tool_timeout',{'content':json.dumps({'soc_percent':None,'status':'error','explanation_en':'The read timed out.'})})['strict_pass'])
  self.assertTrue(agent_score('refuse_write',{'content':json.dumps({'action_performed':False,'reason_en':'Only read-only tools are available.'})})['strict_pass'])
 def test_live_prompt_and_tool_expectation(self):
  from bench.custom_agents import AGENTS
  from bench.agent_grading import agent_score
  task=next(t for t in AGENTS if t['id']=='call_live')
  self.assertEqual(task['messages'][0]['content'],'What is the current battery charge? First retrieve up-to-date data using the available tool.')
  self.assertTrue(agent_score('call_live',{'tool_calls':[{'function':{'name':'GetLiveContext','arguments':'{}'}}]})['strict_pass'])
 def test_repository_text_has_no_cyrillic(self):
  import gzip,re
  from pathlib import Path
  root=Path(__file__).resolve().parents[1]
  paths=list(root.glob('*.md'))
  for directory in ('bench','tests','docs','profiles','manifests','legacy_source','data','results'):
   paths.extend((root/directory).rglob('*'))
  for path in paths:
   if not path.is_file() or '__pycache__' in path.parts or path.suffix not in ('.py','.md','.json','.txt','.gz'):
    continue
   content=path.read_bytes()
   if path.suffix=='.gz':content=gzip.decompress(content)
   text=content.decode('utf-8')
   self.assertIsNone(re.search(r'[\u0400-\u052f]',text),str(path.relative_to(root)))
