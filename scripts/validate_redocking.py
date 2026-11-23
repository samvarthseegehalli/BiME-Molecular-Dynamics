#!/usr/bin/env python3
"""Measure HDOCK redocking recovery against an experimental complex."""

from __future__ import annotations

import argparse
import csv
import glob
import itertools
import os
import re
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Atom:
    chain: str
    resseq: int
    icode: str
    resname: str
    name: str
    xyz: np.ndarray

    @property
    def atom_key(self):
        return (self.chain, self.resseq, self.icode, self.resname, self.name)

    @property
    def residue_key(self):
        return (self.chain, self.resseq, self.icode, self.resname)


def read_atoms(path: str) -> list[Atom]:
    atoms = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("ATOM  "):
                continue
            altloc = line[16]
            if altloc not in (" ", "A"):
                continue
            try:
                atoms.append(
                    Atom(
                        chain=line[21].strip(),
                        resseq=int(line[22:26]),
                        icode=line[26].strip(),
                        resname=line[17:20].strip(),
                        name=line[12:16].strip(),
                        xyz=np.array(
                            [float(line[30:38]), float(line[38:46]), float(line[46:54])],
                            dtype=float,
                        ),
                    )
                )
            except ValueError:
                continue
    return atoms


def chain_set(text: str) -> set[str]:
    return {character for character in text if character not in {",", " ", ":"}}


def select(atoms: list[Atom], chains: set[str]) -> list[Atom]:
    return [atom for atom in atoms if atom.chain in chains]


def kabsch(reference: np.ndarray, mobile: np.ndarray):
    """Return row-vector transform mapping reference coordinates onto mobile."""
    ref_center = reference.mean(axis=0)
    mob_center = mobile.mean(axis=0)
    covariance = (reference - ref_center).T @ (mobile - mob_center)
    u, _, vt = np.linalg.svd(covariance)
    rotation = u @ vt
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vt
    translation = mob_center - ref_center @ rotation
    return rotation, translation


def matched_coordinates(reference: list[Atom], mobile: list[Atom], atom_name="CA"):
    ref = {atom.atom_key: atom.xyz for atom in reference if atom.name == atom_name}
    mob = {atom.atom_key: atom.xyz for atom in mobile if atom.name == atom_name}
    keys = sorted(ref.keys() & mob.keys())
    if len(keys) < 3:
        raise ValueError(f"only {len(keys)} matching {atom_name} atoms")
    return keys, np.array([ref[key] for key in keys]), np.array([mob[key] for key in keys])


def residue_contacts(receptor: list[Atom], ligand: list[Atom], cutoff=5.0):
    contacts = set()
    cutoff2 = cutoff * cutoff
    ligand_grid = {}
    for atom in ligand:
        if not atom.name.startswith("H"):
            cell = tuple(np.floor(atom.xyz / cutoff).astype(int))
            ligand_grid.setdefault(cell, []).append(atom)
    offsets = tuple(itertools.product((-1, 0, 1), repeat=3))
    for rec_atom in receptor:
        if rec_atom.name.startswith("H"):
            continue
        cell = tuple(np.floor(rec_atom.xyz / cutoff).astype(int))
        for offset in offsets:
            neighbor = tuple(cell[i] + offset[i] for i in range(3))
            for lig_atom in ligand_grid.get(neighbor, ()):
                delta = rec_atom.xyz - lig_atom.xyz
                if float(delta @ delta) <= cutoff2:
                    contacts.add((rec_atom.residue_key, lig_atom.residue_key))
    return contacts


def model_rank(path: str) -> int:
    match = re.search(r"model_(\d+)\.pdb$", path)
    return int(match.group(1)) if match else 10**9


def remarks(path: str):
    score = float("nan")
    server_rmsd = float("nan")
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("REMARK Score:"):
                score = float(line.split()[-1])
            elif line.startswith("REMARK RMSD:"):
                server_rmsd = float(line.split()[-1])
            elif line.startswith("ATOM"):
                break
    return score, server_rmsd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--receptor-chains", required=True)
    parser.add_argument("--ligand-chains", required=True)
    parser.add_argument("--models-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    receptor_chains = chain_set(args.receptor_chains)
    ligand_chains = chain_set(args.ligand_chains)
    reference_atoms = read_atoms(args.reference)
    reference_receptor = select(reference_atoms, receptor_chains)
    reference_ligand = select(reference_atoms, ligand_chains)
    native_contacts = residue_contacts(reference_receptor, reference_ligand)
    native_epitope = {pair[0] for pair in native_contacts}

    rows = []
    for path in sorted(glob.glob(os.path.join(args.models_dir, "model_*.pdb")), key=model_rank):
        model_atoms = read_atoms(path)
        model_receptor = select(model_atoms, receptor_chains)
        model_ligand = select(model_atoms, ligand_chains)

        _, ref_rec_ca, model_rec_ca = matched_coordinates(reference_receptor, model_receptor)
        rotation, translation = kabsch(ref_rec_ca, model_rec_ca)
        _, ref_lig_ca, model_lig_ca = matched_coordinates(reference_ligand, model_ligand)
        transformed_native_ligand = ref_lig_ca @ rotation + translation
        lrmsd = float(np.sqrt(np.mean(np.sum((transformed_native_ligand - model_lig_ca) ** 2, axis=1))))

        predicted_contacts = residue_contacts(model_receptor, model_ligand)
        recovered = native_contacts & predicted_contacts
        fnat = len(recovered) / len(native_contacts) if native_contacts else float("nan")
        predicted_epitope = {pair[0] for pair in predicted_contacts}
        epitope_recall = len(native_epitope & predicted_epitope) / len(native_epitope) if native_epitope else float("nan")
        epitope_precision = len(native_epitope & predicted_epitope) / len(predicted_epitope) if predicted_epitope else 0.0
        score, server_rmsd = remarks(path)
        rows.append(
            {
                "rank": model_rank(path),
                "score": f"{score:.2f}",
                "server_initial_orientation_rmsd_A": f"{server_rmsd:.2f}",
                "ligand_rmsd_A": f"{lrmsd:.3f}",
                "fnat": f"{fnat:.4f}",
                "epitope_recall": f"{epitope_recall:.4f}",
                "epitope_precision": f"{epitope_precision:.4f}",
                "native_contact_count": len(native_contacts),
                "recovered_native_contacts": len(recovered),
                "predicted_contact_count": len(predicted_contacts),
                "model": os.path.basename(path),
            }
        )

    if not rows:
        raise SystemExit("no model_*.pdb files found")
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
