#!/usr/bin/env python3
"""Explicit single-stage, checkpoint-resumable runner; default is dry-run.

This script never launches the next stage automatically. Review the preceding
stage's physical diagnostics before acknowledging it on the command line.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [18473, 59107, 87311, 23197, 64489]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complete(gmx, stage, run, basename, tpr):
    if stage=='em':
        log=run/'em.log'
        return log.exists() and bool(re.search(r'converged to Fmax <',log.read_text()))
    cpt=run/f'{basename}.cpt'
    if not cpt.exists():
        return False
    def dump(arguments):
        result=subprocess.run([gmx,'dump']+arguments,text=True,capture_output=True,check=True)
        return result.stdout+result.stderr
    settings=dump(['-s',str(tpr)])
    checkpoint=dump(['-cp',str(cpt)])
    steps=int(re.search(r'\bnsteps\s*=\s*(\d+)',settings).group(1))
    initial=int(re.search(r'\binit-step\s*=\s*(\d+)',settings).group(1))
    current=int(re.search(r'\bstep\s*=\s*(\d+)',checkpoint).group(1))
    return current>=initial+steps


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('system', type=Path)
    p.add_argument('stage', choices=['em','nvt','npt','pilot','production'])
    p.add_argument('--replica', type=int, default=1, choices=range(1,6))
    p.add_argument('--execute', action='store_true')
    p.add_argument('--reviewed-previous-stage', action='store_true', help='acknowledge physical QC, not merely file existence')
    p.add_argument('--gmx', default=os.environ.get('GMX_CMD','gmx'))
    p.add_argument('--mdrun-args', default=os.environ.get('MDRUN_EXTRA','-ntmpi 1 -ntomp 8'))
    p.add_argument('--maxh', type=float, default=23.5, help='checkpoint before instance wall time; rerun same command to resume')
    args=p.parse_args()
    if (ROOT/'gromacs-topology').is_dir():
        os.environ['GMXLIB']=str(ROOT/'gromacs-topology')
    system=args.system.resolve()
    if not (system/'topol.top').is_file():
        p.error('system directory must contain topol.top')
    stage=args.stage
    run=system if stage=='em' else system/f'replica-{args.replica:02d}'
    basename='md_20ns' if stage=='production' else stage
    tpr=run/f'{basename}.tpr'
    coordinate=run/f'{basename}.gro'
    checkpoint=run/f'{basename}.cpt'
    stamp=run/f'{basename}.stage.json'
    mdp=None
    if stage!='em':
        source='production_20ns.mdp' if stage in ('pilot','production') else stage+'.mdp'
        mdp=(ROOT/'mdp'/source).read_text()
        if stage=='nvt':
            mdp=mdp.replace('gen_seed = -1',f'gen_seed = {SEEDS[args.replica-1]}')
        if stage=='pilot':
            mdp=mdp.replace('nsteps = 10000000','nsteps = 50000')
        previous={'nvt':system/'em','npt':run/'nvt','pilot':run/'npt','production':run/'pilot'}[stage]
        prior_gro=previous.with_suffix('.gro')
        if args.execute and not args.reviewed_previous_stage:
            p.error('review preceding-stage QC, then supply --reviewed-previous-stage')
        if args.execute and not prior_gro.exists():
            p.error(f'preceding stage has not finished: {prior_gro}')
        prior_stage={'nvt':'em','npt':'nvt','pilot':'npt','production':'pilot'}[stage]
        if args.execute and not complete(args.gmx,prior_stage,previous.parent,previous.name,previous.with_suffix('.tpr')):
            p.error('preceding stage is incomplete or minimization did not meet Fmax; review and resolve before advancing')
    else:
        if not tpr.exists():
            p.error('missing em.tpr')
    command=[args.gmx,'mdrun','-deffnm',basename,'-s',str(tpr),'-maxh',str(args.maxh)]+shlex.split(args.mdrun_args)
    if checkpoint.exists():
        command+=['-cpi',str(checkpoint),'-append']
    print(f'Working directory: {run}')
    print(('EXECUTE: ' if args.execute else 'DRY RUN: ')+shlex.join(command),flush=True)
    if not args.execute:
        print('No files changed; no MD launched. One stage only.')
        return
    run.mkdir(exist_ok=True)
    if coordinate.exists() and complete(args.gmx,stage,run,basename,tpr):
        raise SystemExit(f'Stage already complete: {coordinate}. Inspect outputs; refusing overwrite.')
    if coordinate.exists() and not checkpoint.exists():
        raise SystemExit('Existing coordinates without a resumable checkpoint; inspect failed/incomplete run.')
    record={'stage':stage,'replica':args.replica,'topology_sha256':digest(system/'topol.top'),
            'restraints_sha256':digest(system/'posre.itp'), 'mdp_sha256':hashlib.sha256(mdp.encode()).hexdigest() if mdp else None}
    if stamp.exists():
        existing=json.loads(stamp.read_text())
        if any(existing.get(k)!=v for k,v in record.items()):
            raise SystemExit('Inputs changed since this stage started; refusing unsafe resume.')
        if existing.get('tpr_sha256')!=digest(tpr):
            raise SystemExit('TPR changed since this stage started; refusing unsafe resume.')
    elif stage!='em' and tpr.exists():
        raise SystemExit('Untracked TPR exists; inspect it before running this stage.')
    if stage!='em' and not tpr.exists():
        f=run/f'{basename}.mdp'
        f.write_text(mdp)
        cmd=[args.gmx,'grompp','-f',str(f),'-c',str(prior_gro),'-p',str(system/'topol.top'),'-o',str(tpr),'-po',str(run/f'{basename}.mdout.mdp')]
        if stage in ('nvt','npt'):
            cmd+=['-r',str(system/'em.gro')]
        if stage!='nvt':
            cmd+=['-t',str(previous.with_suffix('.cpt'))]
        with (run/f'{basename}.grompp.log').open('w') as log:
            subprocess.run(cmd,cwd=system,stdout=log,stderr=subprocess.STDOUT,check=True)
    record['tpr_sha256']=digest(tpr)
    record['last_launch_utc']=datetime.now(timezone.utc).isoformat()
    record['command']=command
    stamp.write_text(json.dumps(record,indent=2)+'\n')
    with (run/f'{basename}.console.log').open('a') as log:
        result=subprocess.run(command,cwd=run,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(result.returncode)
    if not coordinate.exists() or not complete(args.gmx,stage,run,basename,tpr):
        raise SystemExit('Stage stopped before completion; inspect its checkpoint/log and resolve it before any later stage.')
    print('Stage returned successfully. Review energies, constraints and geometry before advancing.')


if __name__=='__main__':
    main()
