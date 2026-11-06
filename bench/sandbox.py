"""Bubblewrap isolation: fail closed, no home/network, bounded process/resources.

This is a local defense-in-depth test sandbox, not a VM or a claim that an
unpatched host kernel is safe against arbitrary hostile machine code.
"""
import os, pathlib, resource, shutil, signal, subprocess, tempfile, time, secrets

def _limits():
    resource.setrlimit(resource.RLIMIT_CPU,(5,5))
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1024**2,1024**2))
    resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))

def execute(source, timeout=8):
    if not shutil.which('bwrap'): raise RuntimeError('bubblewrap required; no unsafe fallback')
    with tempfile.TemporaryDirectory(prefix='modelbench-') as folder:
        p=pathlib.Path(folder); marker='BENCH_COMPLETE_'+secrets.token_hex(24)
        bootstrap='import resource\nresource.setrlimit(resource.RLIMIT_NPROC,(0,0))\nexec(compile('+repr(source)+', \"candidate\", \"exec\"))\nprint('+repr(marker)+')\n'
        (p/'candidate.py').write_text(bootstrap)
        command=['bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL',
                 '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib']
        if pathlib.Path('/lib64').exists(): command += ['--ro-bind','/lib64','/lib64']
        command += ['--proc','/proc','--dir','/dev','--dev-bind','/dev/null','/dev/null','--dev-bind','/dev/urandom','/dev/urandom','--size',str(16*1024**2),'--tmpfs','/tmp','--dir','/work',
                    '--ro-bind',str(p/'candidate.py'),'/work/candidate.py',
                    '--remount-ro','/','--chdir','/work','--clearenv','--setenv','PATH','/usr/bin',
                    '--setenv','HOME','/tmp','/usr/bin/python3','-I','-B','/work/candidate.py']
        start=time.monotonic(); timed_out=False
        with open(p/'stdout','wb') as out,open(p/'stderr','wb') as err:
            proc=subprocess.Popen(command,stdout=out,stderr=err,preexec_fn=_limits,start_new_session=True)
            try: proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out=True
                os.killpg(proc.pid,signal.SIGKILL); proc.wait()
        stderr=(p/'stderr').read_bytes()[:16000].decode(errors='replace')
        if 'bwrap:' in stderr: raise RuntimeError('Sandbox unavailable: '+stderr)
        return {'passed':proc.returncode==0 and not timed_out and marker in (p/'stdout').read_text(errors='replace'),'returncode':proc.returncode,
                'timeout':timed_out,'wall_s':round(time.monotonic()-start,4),
                'stdout':(p/'stdout').read_bytes()[:16000].decode(errors='replace'),'stderr':stderr}
