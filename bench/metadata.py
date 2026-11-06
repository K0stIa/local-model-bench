import hashlib,pathlib,subprocess

def source_digest(root):
    root=pathlib.Path(root);digest=hashlib.sha256()
    for dirname in ('bench','profiles','data'):
        for p in sorted((root/dirname).rglob('*')) if (root/dirname).exists() else []:
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo'):
                digest.update(str(p.relative_to(root)).encode()+b'\0'+p.read_bytes()+b'\0')
    return digest.hexdigest()

def git_state(root):
    try:
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
        dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True))
        return {'git_commit':commit,'git_dirty':dirty}
    except subprocess.CalledProcessError:return {'git_commit':None,'git_dirty':True}
