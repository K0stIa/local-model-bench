import copy,gzip,hashlib,json,pathlib
from .core import extract_code
from .sandbox import execute
from .agent_grading import agent_score
ROOT=pathlib.Path(__file__).resolve().parent.parent

def load_suite(name):
    if name=='humaneval':
        path=ROOT/'data/humaneval/HumanEval.jsonl.gz'
        if hashlib.sha256(path.read_bytes()).hexdigest()!='b796127e635a67f93fb35c04f4cb03cf06f38c8072ee7cee8833d7bee06979ef':
            raise ValueError('HumanEval source hash mismatch')
        with gzip.open(path,'rt') as f: rows=[json.loads(x) for x in f]
        return [{'id':r['task_id'],'kind':'humaneval','messages':[{'role':'user','content':'Complete this Python function. Return the complete runnable function including its signature and necessary imports, without Markdown or prose.\n'+r['prompt']}],'source':r} for r in rows]
    if name!='custom': raise ValueError(name)
    from .custom_coding import TASKS
    from .custom_agents import AGENTS
    out=[{'id':'code_'+t['id'],'kind':'code','messages':[{'role':'user','content':'Implement Python 3. Return only runnable function code, no markdown or prose. Standard-library imports are permitted. Do not mutate inputs. '+t['spec']}],'source':t} for t in TASKS]
    out += [dict(id='agent_'+t['id'],kind='agent',**{k:copy.deepcopy(v) for k,v in t.items() if k!='id'}) for t in AGENTS if t['id']!='unavailable']
    out.append({'id':'agent_unavailable_v2','kind':'agent','messages':[{'role':'user','content':'Return JSON only with offline_devices and auxiliary_unavailable. Device availability is determined ONLY by the explicit availability field: offline means proven offline, unknown does not. Auxiliary means ONLY entries marked auxiliary:true. List offline device names and unavailable auxiliary entity IDs, sorted. Data: {"devices":{"kettle":{"availability":"online"},"router":{"availability":"online"},"bedroom":{"availability":"unknown"},"balcony":{"availability":"offline"}},"entities":[{"id":"kettle.switch","state":"on","auxiliary":false},{"id":"kettle.child_lock","state":"unavailable","auxiliary":true},{"id":"bedroom.temperature","state":"unavailable","auxiliary":false},{"id":"balcony.temperature","state":"unavailable","auxiliary":false}]}'}]})
    records='\n'.join('sensor_%03d = %d units; timestamp %d'%(i,(i*17)%101,1700000000+i) for i in range(150))+'\nsensor_017 = 93 units; timestamp 1700001000\nsensor_083 = 12 units; timestamp 1700001001\n'
    out.append({'id':'agent_long_context','kind':'agent','messages':[{'role':'user','content':'Read the synthetic log below. Return JSON only with s17, s83, s149, using the LAST occurrence of each corresponding sensor. No explanation.\n'+records}]})
    return out

def grade(task,msg):
    if task['kind']=='agent': return agent_score(task['id'][6:],msg)
    code,strict=extract_code(msg.get('content') or '')
    source='candidate_ns={}\nexec(compile('+repr(code)+', "candidate", "exec"),candidate_ns)\n'
    if task['kind']=='humaneval':
        row=task['source']
        source+='test_ns=dict(candidate_ns)\nexec(compile('+repr(row['test'])+', "tests", "exec"),test_ns)\ntest_ns["check"](candidate_ns['+repr(row['entry_point'])+'])\n'
    else:
        t=task['source']
        helper=(ROOT/'bench/suites_equal.py').read_text()
        source+=helper+'\nimport copy\ncases='+repr(t['cases'])+'\n'
        source+='for args, expected in cases:\n    supplied=copy.deepcopy(args)\n    before=copy.deepcopy(supplied)\n    actual=candidate_ns['+repr(t['name'])+'](*supplied)\n    assert eq(actual,expected), (actual,expected)\n    assert eq(supplied,before), "input mutated"\n'
        if t['id']=='patch':
            source+='def mutable_ids(x):\n    result={id(x)} if isinstance(x,(dict,list,set)) else set()\n    if isinstance(x,(dict,list,tuple,set)):\n        for y in (x.values() if isinstance(x,dict) else x): result |= mutable_ids(y)\n    return result\nfor args, expected in cases:\n    supplied=copy.deepcopy(args)\n    result=candidate_ns["merge_patch"](*supplied)\n    assert not mutable_ids(result)&mutable_ids(supplied), "aliased input"\n'
    score=execute(source)
    passed=score['passed']
    return {'functional_pass':passed,'strict_pass':passed and strict,'execution':score}
