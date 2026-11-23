#!/usr/bin/env python3
"""GROMACS analysis with explicit groups and ps input windows; dry-run by default.

Provides fold/motion traces and interface contact/H-bond counts. Reference-contact
occupancy, H-bond occupancy, BSA and replica statistics require subsequent analysis.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('replica',type=Path)
    p.add_argument('--basename',default='md_20ns')
    p.add_argument('--start-ns',type=float,default=0)
    p.add_argument('--gmx',default='gmx')
    p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    replica=a.replica.resolve();system=replica.parent
    index=system/'analysis.ndx'
    metadata=json.loads((system/'analysis_groups.json').read_text())
    out=replica/f'analysis_from_{a.start_ns:g}ns'
    tpr=replica/f'{a.basename}.tpr';xtc=replica/f'{a.basename}.xtc'
    whole=out/'protein_nojump.xtc'
    start_ps=str(a.start_ns*1000)
    if a.execute:
        if not tpr.exists() or not xtc.exists():
            p.error('completed trajectory and matching TPR required')
        out.mkdir(exist_ok=True)
    def run(name,cmd,selection=''):
        command=[a.gmx]+cmd
        print(shlex.join(command),flush=True)
        if a.execute:
            with (out/f'{name}.log').open('w') as log:
                subprocess.run(command,input=selection,text=True,stdout=log,stderr=subprocess.STDOUT,check=True)
    # Use full time history for nojump; apply analysis windows only afterwards.
    run('pbc',['trjconv','-s',str(tpr),'-f',str(xtc),'-n',str(index),'-pbc','nojump','-o',str(whole)],'Protein\n')
    common=['-s',str(tpr),'-f',str(whole),'-n',str(index),'-b',start_ps]
    selections=['Construct_CA']+sorted(g for g in metadata['groups'] if g.startswith('Domain') and g.endswith('_CA'))
    for group in selections:
        # Default time unit is ps; convert units explicitly in downstream plots.
        run(group+'_rmsd',['rms']+common+['-o',str(out/f'{group}_rmsd_nm.xvg')],group+'\n'+group+'\n')
        run(group+'_rmsf',['rmsf']+common+['-res','-o',str(out/f'{group}_rmsf_nm.xvg')],group+'\n')
    run('construct_rg',['gyrate']+common+['-sel','group "Construct"','-o',str(out/'construct_rg_nm.xvg')])
    run('construct_sasa',['sasa']+common+['-surface','group "Protein"','-output','group "Construct"','-o',str(out/'construct_sasa_in_complex_nm2.xvg')])
    for number,target in ((1,'X'),(2,'Y')):
        if f'Target_{target}' not in metadata['groups']:
            continue
        selection=f'Arm{number}\nTarget_{target}\n'
        run(f'interface_{target}_contacts',['mindist']+common+['-d','0.45','-od',str(out/f'interface_{target}_minimum_nm.xvg'),'-on',str(out/f'interface_{target}_atom_contacts.xvg')],selection)
        run(f'interface_{target}_hbonds',['hbond-legacy']+common+['-r','0.35','-a','30','-num',str(out/f'interface_{target}_hbond_counts.xvg')],selection)
    if a.execute:
        (out/'ANALYSIS_SCOPE.txt').write_text('Times are ps; distances nm; SASA nm^2. Nojump requires visual/continuity checks. Domain RMSDs use independent fits. Interface contacts here are atom-pair counts, not native-contact fractions. H-bond counts are not per-bond occupancies. Do not pool frames as independent replicates. BSA, reference-contact and H-bond occupancy, and replica statistics remain separate analyses.\n')


if __name__=='__main__':
    main()
