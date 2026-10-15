"""Record this local experiment and safely restore its exact pre-change checkpoint."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='64066fa68977aa17c1cf2c74378d4e76cebff6eb'
STATE=ROOT/'.recovery/shared-region-names.json'

def git(*args, **kwargs):
    return subprocess.run(['git',*args],cwd=ROOT,check=True,stdout=subprocess.PIPE,**kwargs).stdout

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def record():
    if STATE.exists(): raise SystemExit('A recovery record already exists; do not overwrite it.')
    tracked=git('diff','--name-only','-z',BASE).decode().strip('\0').split('\0')
    new=git('ls-files','--others','--exclude-standard','-z').decode().strip('\0').split('\0')
    files={name:{'new':name in new,'applied_sha256':digest(ROOT/name)} for name in tracked+new if name}
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({'checkpoint':BASE,'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Recorded {len(files)} changed paths for exact local rollback. No ZIP created.')

def inspect():
    data=json.loads(STATE.read_text(encoding='utf-8'))
    for name,info in data['files'].items():
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT): raise SystemExit('Unsafe recovery path')
        if digest(path)!=info['applied_sha256']:
            raise SystemExit(f'Later changes detected in {name}; preserve them before restoring.')
    git('cat-file','-e',data['checkpoint']+'^{commit}')
    return data

def restore():
    data=inspect()
    tracked=[name for name,info in data['files'].items() if not info['new']]
    paths=STATE.parent/'restore-paths.txt'
    paths.write_bytes(b'\0'.join(name.encode() for name in tracked)+b'\0')
    git('restore','--source='+data['checkpoint'],'--worktree','--pathspec-from-file='+str(paths),'--pathspec-file-nul')
    for name,info in data['files'].items():
        if info['new']:
            (ROOT/name).unlink(missing_ok=True)
    print('Restored the exact pre-experiment local files. GitHub and Cloudflare untouched.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--record',action='store_true')
    parser.add_argument('--restore',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if sum([args.record,args.restore,args.check])!=1: parser.error('Choose --record, --check or --restore')
    if args.record: record()
    elif args.restore: restore()
    else:
        data=inspect()
        print(f'PASS: checkpoint and {len(data["files"])} file hashes verified; ready for rollback.')
