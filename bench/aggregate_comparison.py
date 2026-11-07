"""Export only aggregate metrics, never requests, responses, logs or host paths."""
import argparse, json, math, pathlib, statistics
GROUPS={'coding':'code_','agents':'agent_','humaneval':'HumanEval/'}
def distribution(values):
    v=[x for x in values if type(x) in (int,float) and math.isfinite(x)]
    return {'n':len(v),'min':min(v),'median':statistics.median(v),'max':max(v)} if v else {'n':0}
def summarize(rows):
    output={}
    for name,prefix in GROUPS.items():
        selected=[r for r in rows if r['task'].startswith(prefix)]
        if len({r['task'] for r in selected})!=len(selected):raise ValueError('Duplicate task; split repeats before aggregation')
        output[name]={'attempted':len(selected),'functional':sum(bool(r.get('score',{}).get('functional_pass')) for r in selected),
          'strict':sum(bool(r.get('score',{}).get('strict_pass')) for r in selected),
          'truncated':sum(r.get('finish_reason')=='length' for r in selected),'errors':sum('error' in r for r in selected),
          'execution_timeouts':sum(bool(r.get('score',{}).get('execution',{}).get('timeout')) for r in selected),
          'wall_seconds':distribution([r.get('wall_s') for r in selected]),
          'prefill_tokens_per_second':distribution([r.get('response',{}).get('timings',{}).get('prompt_per_second') for r in selected]),
          'decode_tokens_per_second':distribution([r.get('response',{}).get('timings',{}).get('predicted_per_second') for r in selected]),
          'prompt_tokens':distribution([r.get('response',{}).get('usage',{}).get('prompt_tokens') for r in selected]),
          'completion_tokens':distribution([r.get('response',{}).get('usage',{}).get('completion_tokens') for r in selected])}
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-root',required=True);p.add_argument('--output',required=True);p.add_argument('--include-native',action='store_true');a=p.parse_args()
    names=['qwen35-english','devstral-english','glm-english','laguna-english','twil-english']
    if a.include_native:names.append('twil-native')
    models={};matched=[]
    for name in names:
        rows=[];manifests=[]
        for file in sorted((pathlib.Path(a.input_root)/name).glob('*.jsonl')):
            data=[json.loads(line) for line in file.read_text().splitlines()]
            rows.extend(r for r in data if r.get('type')=='result');manifests.extend(r for r in data if r.get('type')=='manifest')
        summary=summarize(rows)
        if [summary[g]['attempted'] for g in GROUPS]!=[9,10,10]:raise ValueError('Incomplete run: '+name)
        if len(manifests)!=2:raise ValueError('Expected custom + HumanEval manifests')
        for m in manifests:
            if name!='twil-native':matched.append((m['profile'],m['source_sha256'],m['seed'],m['timeout']))
        models[name]={'metrics':summary,'profile':manifests[0]['profile'],'source_sha256':manifests[0]['source_sha256'],'task_ids':sorted(r['task'] for r in rows)}
    if any(x!=matched[0] for x in matched):raise ValueError('Practical profile/source/seed/timeout mismatch')
    result={'protocol':'matched-English-chat-v1','repeats':1,'models':models,
            'limitations':['Small smoke suite, not official HumanEval pass@1.','Timing distributions span different tasks and outputs; not repeated fixed-workload performance trials.','Prefix cache, tokenization and response length affect timings.','Native4096 is a separate budget and sampling track.']}
    with open(a.output,'x') as f:json.dump(result,f,indent=2);f.write('\n')
if __name__=='__main__':main()
