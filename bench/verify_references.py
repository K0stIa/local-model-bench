"""Validate datasets/grader without model inference. No live Home Assistant."""
import inspect
from .suites import load_suite,grade

def main():
    for task in load_suite('humaneval'):
        row=task['source']
        score=grade(task,{'content':row['prompt']+row['canonical_solution']})
        assert score['functional_pass'],(task['id'],score)
    print('HumanEval canonical: 164/164')
    for task in load_suite('custom'):
        if task['kind']!='code':continue
        ref=task['source']['ref'];name=task['source']['name']
        code='import copy,itertools,math\n'+inspect.getsource(ref).replace('def '+ref.__name__+'(','def '+name+'(',1)
        if ref.__name__=='patch':code+='\npatch=merge_patch\n'
        score=grade(task,{'content':code})
        assert score['functional_pass'],(task['id'],score)
    print('Custom references: 9/9 (168 cases)')
if __name__=='__main__':main()
