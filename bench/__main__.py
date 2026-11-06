import argparse,datetime,hashlib,json,pathlib,platform,subprocess,time
from .client import validate_endpoint,ensure_idle,build_body,complete
from .core import select_tasks
from .suites import load_suite,grade
from .metadata import source_digest,git_state

def main():
    p=argparse.ArgumentParser(description='Local-only model benchmark; generated code runs in bubblewrap')
    sub=p.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run');run.add_argument('--endpoint',required=True);run.add_argument('--model',required=True)
    run.add_argument('--suite',choices=['custom','humaneval'],default='custom');run.add_argument('--limit',type=int,default=20)
    run.add_argument('--seed',type=int,default=42);run.add_argument('--repeat',type=int,default=1)
    run.add_argument('--profile',type=pathlib.Path,required=True);run.add_argument('--output',type=pathlib.Path,required=True)
    run.add_argument('--timeout',type=float,default=120);run.add_argument('--budget',type=float,default=1200)
    run.add_argument('--task',action='append',help='Exact task id, repeat to choose multiple')
    run.add_argument('--runtime-manifest',type=pathlib.Path,help='Sanitized JSON manifest: GGUF hash/revision, runtime and server flags')
    run.add_argument('--dry-run',action='store_true')
    ls=sub.add_parser('list');ls.add_argument('--suite',choices=['custom','humaneval'],default='custom')
    report=sub.add_parser('report');report.add_argument('path',type=pathlib.Path)
    args=p.parse_args()
    if args.command=='report':
        rows=[json.loads(x) for x in args.path.read_text().splitlines()]
        scores=[r for r in rows if r.get('type')=='result']
        print(json.dumps({'attempted':len(scores),'functional':sum(r.get('score',{}).get('functional_pass',False) for r in scores),'strict':sum(r.get('score',{}).get('strict_pass',False) for r in scores),'errors':sum('error' in r for r in scores),'truncated':sum(r.get('finish_reason')=='length' for r in scores),'wall_seconds':sum(r['wall_s'] for r in scores)},indent=2));return
    tasks=load_suite(args.suite)
    if args.command=='list':
        for t in tasks:print(t['id'],t['kind'])
        return
    if args.task:
        wanted=set(args.task);known={t['id'] for t in tasks}
        if wanted-known:raise ValueError('Unknown task ids: '+str(wanted-known))
        tasks=[t for t in tasks if t['id'] in wanted]
    tasks=select_tasks(tasks,args.limit,args.seed)
    if args.repeat<1 or args.timeout<=0 or args.budget<=0:raise ValueError('repeat/timeout/budget must be positive')
    endpoint=validate_endpoint(args.endpoint);profile=json.loads(args.profile.read_text())
    for task in tasks:build_body(args.model,task,profile)
    if args.dry_run:
        print(json.dumps({'model':args.model,'tasks':[t['id'] for t in tasks],'repeat':args.repeat,'profile':profile,'endpoint':endpoint},indent=2));return
    # Fail closed before spending inference time on an unusable execution backend.
    if any(t['kind']!='agent' for t in tasks):
        from .sandbox import execute
        if not execute('assert True')['passed']:raise RuntimeError('Sandbox preflight failed')
    ensure_idle(endpoint)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    root=pathlib.Path(__file__).resolve().parent.parent
    runtime=json.loads(args.runtime_manifest.read_text()) if args.runtime_manifest else None
    manifest={'type':'manifest','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':args.model,'endpoint':endpoint,'suite':args.suite,'task_ids':[t['id'] for t in tasks],'profile':profile,'seed':args.seed,'repeat':args.repeat,'timeout':args.timeout,'budget':args.budget,'python':platform.python_version(),'platform':platform.platform(),**git_state(root),'source_sha256':source_digest(root),'runtime_manifest':runtime,'runtime_manifest_sha256':hashlib.sha256(args.runtime_manifest.read_bytes()).hexdigest() if args.runtime_manifest else None,'protocol':'chat-function-body-v1'}
    start=time.monotonic()
    with args.output.open('x') as f:
        def emit(record):f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush()
        emit(manifest)
        for repeat in range(args.repeat):
            for task in tasks:
                if time.monotonic()-start>=args.budget:emit({'type':'stop','reason':'time_budget'});return
                prior=ensure_idle(endpoint);body=build_body(args.model,task,profile);tick=time.monotonic()
                rec={'type':'result','model':args.model,'task':task['id'],'repeat':repeat,'loaded_before':prior,'request':body}
                try:
                    result=complete(endpoint,body,min(args.timeout,max(1,args.budget-(tick-start))))
                    rec['wall_s']=round(time.monotonic()-tick,4);rec['response']=result
                    choice=result['choices'][0];rec['finish_reason']=choice.get('finish_reason')
                    rec['score']=grade(task,choice['message'])
                    if rec['finish_reason']=='length':rec['score'].update(functional_pass=False,strict_pass=False,truncated=True)
                except Exception as e:
                    rec['wall_s']=round(time.monotonic()-tick,4);rec['error']=str(e)
                emit(rec);print(json.dumps({k:rec.get(k) for k in ['task','repeat','wall_s','score','error']},ensure_ascii=False),flush=True)
                if 'error' in rec:emit({'type':'stop','reason':'error_requires_inspection'});return
if __name__=='__main__':main()
