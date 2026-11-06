"""Synthetic native llama.cpp timing probe; never starts or changes a server."""
import argparse, datetime, hashlib, json, math, pathlib, platform, threading, time, urllib.request
from .client import OPENER, ensure_idle, validate_endpoint
from .metadata import git_state, source_digest


def snapshot(pid=None):
    result={'loadavg':list(__import__('os').getloadavg())}
    mem={}
    for line in pathlib.Path('/proc/meminfo').read_text().splitlines():
        key,value=line.split(':',1)
        if key in ('MemAvailable','SwapFree','SwapTotal'):mem[key+'_kib']=int(value.split()[0])
    result['system']=mem
    if pid:
        try:
            result['process_kib']={k:int(v.split()[0]) for k,v in (line.split(':',1) for line in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line) if k in ('VmRSS','VmHWM','VmSwap')}
        except FileNotFoundError:result['process_missing']=True
    return result


def body(prompt,profile,cache):
    return {'prompt':prompt,'n_predict':profile['decode_tokens'],'temperature':0,'seed':profile['seed'],
            'ignore_eos':True,'cache_prompt':cache,'stream':False}


def validate_profile(p):
    for k in ('decode_tokens','seed','repeats','prompt_lines','timeout_seconds'):
        if type(p.get(k)) is not int or p[k]<1:raise ValueError('Positive integer required: '+k)
    if p['repeats']>20 or p['timeout_seconds']>600:raise ValueError('Excessive benchmark budget')
    return p


def metrics(r):
    t=r.get('timings',{})
    if not isinstance(t,dict):raise ValueError('Missing llama.cpp timings')
    for k in ('prompt_n','prompt_ms','predicted_n','predicted_ms'):
        if type(t.get(k)) not in (int,float) or not math.isfinite(t[k]) or t[k]<0:raise ValueError('Invalid timing: '+k)
    return {k:t.get(k) for k in ('prompt_n','prompt_ms','prompt_per_second','predicted_n','predicted_ms','predicted_per_second','draft_n','draft_n_accepted')}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--endpoint',required=True);a.add_argument('--profile',default='profiles/performance.json')
    a.add_argument('--runtime-manifest',required=True);a.add_argument('--output',required=True)
    a.add_argument('--prompt-file',help='Synthetic UTF-8 prompt, identical across variants');a.add_argument('--server-pid',type=int);a.add_argument('--dry-run',action='store_true')
    args=a.parse_args();endpoint=validate_endpoint(args.endpoint).removesuffix('/v1')
    if args.server_pid is not None and args.server_pid<=0:raise ValueError('Invalid server PID')
    profile=validate_profile(json.loads(pathlib.Path(args.profile).read_text()))
    runtime_bytes=pathlib.Path(args.runtime_manifest).read_bytes();runtime=json.loads(runtime_bytes)
    prompt='Complete this numbered synthetic list with further numbered short sentences.\n'+''.join(f'{i}: The small robot checks a blue box and records the result.\n' for i in range(profile['prompt_lines']))
    if args.prompt_file:prompt=pathlib.Path(args.prompt_file).read_text(encoding='utf-8')
    root=pathlib.Path(__file__).resolve().parents[1]
    meta={'kind':'metadata','profile':profile,'runtime':runtime,'runtime_sha256':hashlib.sha256(runtime_bytes).hexdigest(),
          'source_sha256':source_digest(root),**git_state(root),'python':platform.python_version(),
          'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'prompt_chars':len(prompt),
          'note':'First request is NOT filesystem-cold. RSS is sampled, excludes GPU/shared allocations. Correctness requires separate bench run.'}
    if args.dry_run:print(json.dumps(meta,indent=2));return
    ensure_idle(endpoint)
    with open(args.output,'x') as f:
        def save(r):f.write(json.dumps(r)+'\n');f.flush()
        save(meta)
        for index,cache in enumerate([False]*(profile['repeats']+1)+[True]*profile['repeats']):
            ensure_idle(endpoint);samples=[snapshot(args.server_pid)];stop=threading.Event()
            def sample():
                while not stop.wait(.25):samples.append(snapshot(args.server_pid))
            thread=threading.Thread(target=sample,daemon=True);thread.start();start=time.monotonic()
            try:
                req=urllib.request.Request(endpoint+'/completion',data=json.dumps(body(prompt,profile,cache)).encode(),headers={'Content-Type':'application/json'})
                with OPENER.open(req,timeout=profile['timeout_seconds']) as response:r=json.load(response)
                record={'kind':'measurement','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output_text':r.get('content',''),'index':index,'phase':'first_request' if index==0 else ('prefix_cache' if cache else 'warm_no_cache'),
                        'cache_prompt':cache,'wall_seconds':time.monotonic()-start,'timings':metrics(r),
                        'output_sha256':hashlib.sha256(r.get('content','').encode()).hexdigest(),
                        'tokens_predicted':r.get('tokens_predicted'),'tokens_evaluated':r.get('tokens_evaluated'),
                        'truncated':r.get('truncated'),'stop_type':r.get('stop_type')}
                if r.get('truncated') is True:raise RuntimeError('Context truncated; comparison invalid')
                if record['timings']['predicted_n']!=profile['decode_tokens']:raise RuntimeError('Incomplete fixed decode budget')
            except Exception as exc:
                save({'kind':'error','index':index,'error':str(exc),'wall_seconds':time.monotonic()-start});raise
            finally:
                stop.set();thread.join();samples.append(snapshot(args.server_pid))
            record['memory_samples']=samples;save(record)

if __name__=='__main__':main()
