#!/usr/bin/env python3
"""Compare modeled binder epitopes with experimental CD47–SIRPα interface.

Reports structural overlap and steric exclusion only. It cannot establish
biological checkpoint inhibition or phagocytosis.
"""
import csv
import argparse
import json
from pathlib import Path

from Bio.Align import PairwiseAligner
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
import numpy as np
from scipy.spatial import cKDTree

from assemble_construct_states import CONFIGS
from qc_construct_relaxation import LINKERS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'checkpoint-interface-audit'
NATIVE=ROOT/'track-a-general-cd47-sirpa/structures/2JJS.pdb'
CORE=('A-FC-001','B-FC-001','B-FC-002','B-FC-004')


def residues(chain):
    return [r for r in chain if r.id[0]==' ']


def sequence(rr):
    return ''.join(seq1(r.resname,custom_map={'UNK':'X'}) for r in rr)


def correspondence(model_rr, reference_rr):
    aligner=PairwiseAligner()
    aligner.mode='global';aligner.match_score=2;aligner.mismatch_score=-1
    aligner.open_gap_score=-5;aligner.extend_gap_score=-0.5
    pairs=[(int(i),int(j)) for i,j in zip(*aligner.align(sequence(model_rr),sequence(reference_rr))[0].indices) if i>=0 and j>=0]
    return [(i,j) for i,j in pairs if 'CA' in model_rr[i] and 'CA' in reference_rr[j]]


def alignment(moving_xyz, fixed_xyz):
    moving=np.asarray(moving_xyz);fixed=np.asarray(fixed_xyz)
    cm=moving.mean(0);cf=fixed.mean(0)
    u,_,vt=np.linalg.svd((moving-cm).T@(fixed-cf))
    correction=np.diag([1,1,np.linalg.det(u@vt)])
    rotation=u@correction@vt
    aligned=(moving-cm)@rotation+cf
    rmsd=float(np.sqrt(np.square(aligned-fixed).sum(axis=1).mean()))
    return rotation,cf-cm@rotation,rmsd


def heavy(residue_list):
    return [(r,a) for r in residue_list for a in r if a.element not in ('H','D')]


def contacts(left,right,cutoff=5.0):
    aa,bb=heavy(left),heavy(right)
    tree=cKDTree([a.coord for _,a in bb])
    pairs=set()
    for r,a in aa:
        for j in tree.query_ball_point(a.coord,cutoff):
            pairs.add((r.id[1],bb[j][0].id[1]))
    return pairs


def table(name,rows):
    if not rows:return
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t')
        w.writeheader();w.writerows(rows)


def main():
    parser_args=argparse.ArgumentParser()
    parser_args.add_argument('--native-copy',choices=('AC','BD'),default='AC',help='2JJS biological pair, SIRPα then CD47')
    parser_args.add_argument('--cutoff-A',type=float,choices=(4.0,5.0,6.0),default=5.0)
    args=parser_args.parse_args()
    global OUT
    if args.native_copy!='AC' or args.cutoff_A!=5:
        OUT=OUT/f'{args.native_copy}_{args.cutoff_A:g}A'
    OUT.mkdir(exist_ok=True)
    parser=PDBParser(QUIET=True)
    native=parser.get_structure('native',NATIVE)[0]
    # Two crystallographic biological copies; first letter SIRPα, second CD47.
    sirpa,cd47=args.native_copy
    refs={'SIRPa':(sirpa,cd47),'CD47':(cd47,sirpa)}
    model_rows=[];residue_rows=[];native_rows=[];geometry=[]
    for name in CORE:
        spec=CONFIGS[name]
        path=spec.output/'models'/name/'linker_relaxed_states'/f'{name}_03_dual_bound_linker_relaxed.pdb'
        structure=parser.get_structure(name,path)[0]
        linkers=LINKERS[name]
        arm_boundary=linkers[0] if name in ('B-FC-001','B-FC-002') else linkers[1]
        arm_ranges=((1,arm_boundary[0]-1),(arm_boundary[1]+1,len(residues(structure['A']))))
        for arm_index,(arm,chain_name,(start,end)) in enumerate(zip((spec.arm1,spec.arm2),('X','Y'),arm_ranges),1):
            target=arm.target_name
            if target not in refs:continue
            native_chain,partner_chain=refs[target]
            n_target=residues(native[native_chain]);n_partner=residues(native[partner_chain])
            m_target=residues(structure[chain_name])
            binder=[r for r in structure['A'] if start<=r.id[1]<=end]
            native_pair=contacts(n_target,n_partner,args.cutoff_A)
            native_epitope={r for r,_ in native_pair}
            modeled_pair=contacts(m_target,binder,args.cutoff_A)
            model_epitope={r for r,_ in modeled_pair}
            matches=correspondence(m_target,n_target)
            model_to_native={m_target[i].id[1]:n_target[j].id[1] for i,j in matches}
            native_to_model={n_target[j].id[1]:m_target[i].id[1] for i,j in matches}
            mapped_epitope={model_to_native[i] for i in model_epitope if i in model_to_native}
            overlap=mapped_epitope&native_epitope
            rotation,shift,target_rmsd=alignment([n_target[j]['CA'].coord for i,j in matches],[m_target[i]['CA'].coord for i,j in matches])
            ghost=np.asarray([a.coord for _,a in heavy(n_partner)])@rotation+shift
            binder_xyz=np.asarray([a.coord for _,a in heavy(binder)])
            tree=cKDTree(binder_xyz)
            nearest,_=tree.query(ghost)
            ghost_min=float(nearest.min())
            ghost_clashes=int((nearest<2.0).sum())
            # Native partner transformed to the modeled target's frame; this
            # measures gross steric obstruction of the native binding pose.
            label=f'{name}_arm{arm_index}_{target}'
            row=dict(construct=name,arm=arm_index,target=target,model_target_chain=chain_name,
                     source_target_chain=arm.target_chain,native_target_chain=native_chain,
                     native_partner_chain=partner_chain,aligned_CA_residues=len(matches),
                     identical_aligned_residues=sum(m_target[i].resname==n_target[j].resname for i,j in matches),
                     target_CA_RMSD_A=round(target_rmsd,3),native_interface_residues=len(native_epitope),
                     binder_epitope_residues_mapped=len(mapped_epitope),overlap_residues=len(overlap),
                     native_epitope_overlap_fraction=round(len(overlap)/len(native_epitope),4),
                     binder_epitope_overlap_fraction=round(len(overlap)/len(mapped_epitope),4) if mapped_epitope else 0,
                     ghost_native_partner_min_A=round(ghost_min,3),ghost_native_partner_atoms_under_2A=ghost_clashes,
                     interpretation='structural overlap/exclusion only; no functional inhibition measured')
            model_rows.append(row)
            for native_residue in sorted(native_epitope|mapped_epitope):
                residue_rows.append(dict(construct=name,arm=arm_index,target=target,native_chain=native_chain,
                                         native_author_residue=native_residue,native_name=native[native_chain][native_residue].resname,
                                         model_local_residue=native_to_model.get(native_residue,''),
                                         native_interface=native_residue in native_epitope,
                                         binder_contact=native_residue in mapped_epitope))
            native_rows.append(dict(target=target,native_target_chain=native_chain,native_partner_chain=partner_chain,
                                    native_residue_pairs_5A=len(native_pair),native_interface_residues=len(native_epitope),
                                    native_contact_residues=','.join(map(str,sorted(native_epitope)))))
        if name=='A-FC-001':
            first,second=residues(structure['X']),residues(structure['Y'])
            actual=heavy(first),heavy(second)
            native_min=cKDTree([a.coord for _,a in actual[0]]).query([a.coord for _,a in actual[1]])[0].min()
            geometry.append(dict(construct=name,model_CD47_SIRPa_heavy_min_A=round(float(native_min),3),
                                 note='This prepared dual pose keeps targets apart; it does not represent the native CD47–SIRPα complex.'))
    table('arm_native_overlap.tsv',model_rows)
    table('native_residue_overlap.tsv',residue_rows)
    table('native_interface.tsv',list({r['target']:r for r in native_rows}.values()))
    table('dual_target_geometry.tsv',geometry)
    print(json.dumps(model_rows,indent=2))


if __name__=='__main__':main()
