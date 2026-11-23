#!/usr/bin/env python3
"""Assemble unbound, singly bound and dual-bound BiME starting models.

The script preserves experimentally observed antibody-target interfaces, treats
each arm-target complex as a rigid body, samples opposing-membrane placements,
and builds the explicitly specified glycine-serine linkers with PDBFixer.  The
resulting coordinates are pre-MD hypotheses, not equilibrated structures.
"""

from __future__ import annotations

import argparse
import csv
import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from Bio.Data.IUPACData import protein_letters_3to1
from Bio.PDB.Atom import Atom
from Bio.PDB import Chain, Model, PDBIO, PDBParser, Structure
from Bio.PDB.Residue import Residue
from openmm.app import PDBFile
from pdbfixer import PDBFixer
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation


ROOT = Path(__file__).resolve().parents[1]
AA3 = {key.upper(): value for key, value in protein_letters_3to1.items()}
AA3["MSE"] = "M"
SCFV_LINKER = ["GLY", "GLY", "GLY", "GLY", "SER"] * 3
ARM_LINKER = ["GLY", "GLY", "GLY", "GLY", "SER"] * 4


@dataclass(frozen=True)
class Arm:
    source: Path
    antibody_parts: tuple[tuple[str, int], ...]
    target_chain: str
    target_name: str


@dataclass(frozen=True)
class Construct:
    output: Path
    arm1: Arm
    arm2: Arm


CONFIGS = {
    "A-FC-001": Construct(
        ROOT / "track-a-general-cd47-sirpa/constructs",
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/5TZU.pdb", (("H", 118), ("L", 107)), "C", "CD47"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/6BIT.pdb", (("I", 113), ("K", 106)), "H", "SIRPa"),
    ),
    "A-FC-002": Construct(
        ROOT / "track-a-general-cd47-sirpa/constructs",
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/6BIT.pdb", (("I", 113), ("K", 106)), "H", "SIRPa"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/5TZU.pdb", (("H", 118), ("L", 107)), "C", "CD47"),
    ),
    "B-FC-001": Construct(
        ROOT / "track-b-glioblastoma-targeted/constructs",
        Arm(ROOT / "track-b-glioblastoma-targeted/structures/8UKV.pdb", (("C", 118),), "A", "EGFRvIII"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/6BIT.pdb", (("I", 113), ("K", 106)), "H", "SIRPa"),
    ),
    "B-FC-002": Construct(
        ROOT / "track-b-glioblastoma-targeted/constructs",
        Arm(ROOT / "track-b-glioblastoma-targeted/structures/8UKV.pdb", (("C", 118),), "A", "EGFRvIII"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/5TZU.pdb", (("H", 118), ("L", 107)), "C", "CD47"),
    ),
    "B-FC-003": Construct(
        ROOT / "track-b-glioblastoma-targeted/constructs",
        Arm(ROOT / "track-b-glioblastoma-targeted/complexes/accepted/B-DOCK-001_HuCL47_IL13RA2_rank034_global.pdb", (("H", 119), ("L", 111)), "C", "IL13RA2"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/6BIT.pdb", (("I", 113), ("K", 106)), "H", "SIRPa"),
    ),
    "B-FC-004": Construct(
        ROOT / "track-b-glioblastoma-targeted/constructs",
        Arm(ROOT / "track-b-glioblastoma-targeted/complexes/accepted/B-DOCK-001_HuCL47_IL13RA2_rank034_global.pdb", (("H", 119), ("L", 111)), "C", "IL13RA2"),
        Arm(ROOT / "track-a-general-cd47-sirpa/structures/5TZU.pdb", (("H", 118), ("L", 107)), "C", "CD47"),
    ),
}

# CD47 is on the tumor-cell surface. Track A and the SIRPα-targeting Track B
# designs bridge tumor and macrophage targets (trans); EGFRvIII/IL13RA2 × CD47
# designs co-engage two tumor-cell antigens (cis).
TARGET_RELATIONSHIPS = {
    "A-FC-001": "trans",
    "A-FC-002": "trans",
    "B-FC-001": "trans",
    "B-FC-002": "cis",
    "B-FC-003": "trans",
    "B-FC-004": "cis",
}


def protein_residues(chain, count: int | None = None):
    """Return standard amino-acid residues, optionally limited to the first `count`."""
    residues = [clean_residue(r) for r in chain if r.id[0] == " " and r.resname in AA3]
    return residues if count is None else residues[:count]


def clean_residue(residue):
    """Collapse alternate conformers before any rigid-body transform."""
    result = Residue(residue.id, residue.resname, residue.segid)
    by_name = {}
    for atom in residue.get_unpacked_list():
        by_name.setdefault(atom.name, []).append(atom)
    for name, alternatives in by_name.items():
        chosen = sorted(
            alternatives,
            key=lambda atom: (
                0 if atom.altloc in (" ", "A") else 1,
                -(atom.occupancy or 0.0),
            ),
        )[0]
        # Do not deepcopy a Bio.PDB Atom: its parent links lead back through
        # the full structure hierarchy and make repeated cleanup quadratic.
        atom = Atom(
            chosen.name,
            chosen.coord.copy(),
            chosen.bfactor,
            1.0 if chosen.occupancy is None else chosen.occupancy,
            " ",
            chosen.fullname,
            chosen.serial_number,
            element=chosen.element,
            pqr_charge=getattr(chosen, "pqr_charge", None),
            radius=getattr(chosen, "radius", None),
        )
        result.add(atom)
    return result


def load_arm(spec: Arm):
    """Load an antibody-target complex and return the configured antibody and target chains."""
    model = PDBParser(QUIET=True).get_structure(spec.source.stem, spec.source)[0]
    antibody = [protein_residues(model[chain], count) for chain, count in spec.antibody_parts]
    target = protein_residues(model[spec.target_chain])
    return antibody, target


def atom_coords(residue_groups, heavy_only=True):
    """Return atom coordinates as an (n_atoms, 3) NumPy array; optionally omit hydrogens."""
    coords = []
    for residues in residue_groups:
        for residue in residues:
            for atom in residue:
                if not heavy_only or atom.element != "H":
                    coords.append(atom.coord.copy())
    return np.asarray(coords, dtype=float)


def transform_groups(groups, rotation, origin, destination):
    """Apply a rigid rotation and translation to grouped residues in place."""
    result = deepcopy(groups)
    for residues in result:
        for residue in residues:
            residue.detach_parent()
            for atom in residue:
                atom.coord = rotation.apply(atom.coord - origin) + destination
    return result


def target_anchor(target):
    """Calculate the target fragment anchor coordinates used for placement."""
    cas = np.asarray([r["CA"].coord for r in target if "CA" in r])
    anchor = target[-1]["CA"].coord.copy()
    centroid = cas.mean(axis=0)
    vector = anchor - centroid
    vector /= np.linalg.norm(vector)
    return anchor, vector


def align_vector(source, destination):
    """Return the rotation that aligns one 3D vector with another."""
    return Rotation.align_vectors([destination], [source])[0]


def rotate_about_z(groups, angle, anchor):
    """Rotate residue groups around the z axis through the specified anchor."""
    return transform_groups(groups, Rotation.from_euler("z", angle), anchor, anchor)


def translate_groups(groups, vector):
    """Translate every atom in residue groups by a Cartesian vector in ångströms."""
    result = deepcopy(groups)
    for residues in result:
        for residue in residues:
            residue.detach_parent()
            for atom in residue:
                atom.coord = atom.coord + vector
    return result


def connector_atoms(antibody_parts):
    """Return the terminal antibody atoms used to estimate linker reach."""
    return antibody_parts[-1][-1]["C"].coord.copy(), antibody_parts[0][0]["N"].coord.copy()


def place_complexes(arm1, target1, arm2, target2, relationship="trans"):
    """Place two antibody-target rigid bodies and report clashes and linker geometry."""
    anchor1, vector1 = target_anchor(target1)
    anchor2, vector2 = target_anchor(target2)
    r1 = align_vector(vector1, np.array([0.0, 0.0, -1.0]))
    second_normal = np.array([0.0, 0.0, 1.0 if relationship == "trans" else -1.0])
    r2 = align_vector(vector2, second_normal)

    # Keep arm and antigen in a shared rigid-body transform.
    g1 = transform_groups(arm1 + [target1], r1, anchor1, np.array([0.0, 0.0, -50.0]))
    anchor2_z = 50.0 if relationship == "trans" else -50.0
    base2 = transform_groups(arm2 + [target2], r2, anchor2, np.array([0.0, 0.0, anchor2_z]))
    a1, t1 = g1[:-1], g1[-1]
    p1 = a1[-1][-1]["C"].coord.copy()
    xyz1 = atom_coords(a1 + [t1])
    tree1 = cKDTree(xyz1)
    xyz2_base = atom_coords(base2)
    p2_base0 = base2[0][0]["N"].coord.copy()

    best = None
    separation_values = range(60, 161, 10) if relationship == "trans" else (0,)
    desired = 45.0
    for separation in separation_values:
        shift_z = separation - 100.0 if relationship == "trans" else 0.0
        shift = np.array([0.0, 0.0, shift_z])
        xyz2_shifted = xyz2_base + shift
        p2_shifted = p2_base0 + shift
        anchor2_now = np.array([0.0, 0.0, anchor2_z + shift_z])
        for theta_deg in range(0, 360, 15):
            rotation = Rotation.from_euler("z", math.radians(theta_deg))
            xyz2_turned = rotation.apply(xyz2_shifted - anchor2_now) + anchor2_now
            p2_base = rotation.apply(p2_shifted - anchor2_now) + anchor2_now
            dz = p2_base[2] - p1[2]
            if abs(dz) > 68.0:
                continue
            radial = math.sqrt(max(0.0, desired * desired - dz * dz))
            for phi_deg in range(0, 360, 45):
                phi = math.radians(phi_deg)
                wanted_xy = p1[:2] + radial * np.array([math.cos(phi), math.sin(phi)])
                translation = np.array([wanted_xy[0] - p2_base[0], wanted_xy[1] - p2_base[1], 0.0])
                xyz2 = xyz2_turned + translation
                distances, _ = tree1.query(xyz2, k=1)
                clash20 = int(np.sum(distances < 2.0))
                clash25 = int(np.sum(distances < 2.5))
                minimum = float(distances.min())
                p2 = p2_base + translation
                connector = float(np.linalg.norm(p2 - p1))
                # Favor clash-free, moderately separated rigid bodies while
                # keeping the 20-residue arm linker well below contour length.
                score = (clash20, clash25, -minimum, abs(connector - desired), separation)
                if best is None or score < best[0]:
                    best = (score, separation, theta_deg, phi_deg, connector, minimum, shift, translation)
    if best is None:
        raise RuntimeError("no linker-reachable opposing-membrane placement found")
    _, separation, theta_deg, phi_deg, connector, minimum, shift, translation = best
    placed2 = translate_groups(base2, shift)
    placed2 = rotate_about_z(placed2, math.radians(theta_deg), np.array([0.0, 0.0, 50.0 + shift[2]]))
    placed2 = translate_groups(placed2, translation)
    a2, t2 = placed2[:-1], placed2[-1]
    anchor_separation = float(np.linalg.norm(target_anchor(t1)[0] - target_anchor(t2)[0]))
    return a1, t1, a2, t2, anchor_separation, theta_deg, phi_deg, connector, minimum


def copy_residue(residue, number):
    """Copy a residue and renumber it while preserving atom coordinates and metadata."""
    result = deepcopy(residue)
    result.detach_parent()
    result.id = (" ", number, " ")
    for atom in result:
        if atom.occupancy is None:
            atom.occupancy = 1.0
    return result


def write_gapped(antibody_parts, target1, target2, path):
    """Write a complex PDB with linker gaps reserved between antibody segments."""
    structure = Structure.Structure(path.stem)
    model = Model.Model(0)
    structure.add(model)
    antibody_chain = Chain.Chain("A")
    model.add(antibody_chain)
    missing = {}
    residue_index = 0
    sequence_number = 1
    for part_index, residues in enumerate(antibody_parts):
        for residue in residues:
            antibody_chain.add(copy_residue(residue, sequence_number))
            sequence_number += 1
            residue_index += 1
        if part_index < len(antibody_parts) - 1:
            linker = SCFV_LINKER if part_index in (0, len(antibody_parts) - 2) and len(residues) > 1 else ARM_LINKER
            # Caller inserts explicit linker tokens between parts; this fallback
            # is replaced in build_construct with the exact linker plan.
            missing[(0, residue_index)] = linker
            sequence_number += len(linker)

    for chain_id, residues in (("X", target1), ("Y", target2)):
        chain = Chain.Chain(chain_id)
        model.add(chain)
        for number, residue in enumerate(residues, 1):
            chain.add(copy_residue(residue, number))
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(path))
    return missing


def write_gapped_with_plan(parts, linkers, target1, target2, path):
    """Write an assembled complex and a plan describing linker residues to build."""
    structure = Structure.Structure(path.stem)
    model = Model.Model(0)
    structure.add(model)
    antibody_chain = Chain.Chain("A")
    model.add(antibody_chain)
    missing = {}
    residue_index = 0
    sequence_number = 1
    for i, residues in enumerate(parts):
        for residue in residues:
            antibody_chain.add(copy_residue(residue, sequence_number))
            sequence_number += 1
            residue_index += 1
        if i < len(linkers):
            missing[(0, residue_index)] = linkers[i]
            sequence_number += len(linkers[i])
    for chain_id, residues in (("X", target1), ("Y", target2)):
        chain = Chain.Chain(chain_id)
        model.add(chain)
        for number, residue in enumerate(residues, 1):
            chain.add(copy_residue(residue, number))
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(path))
    return missing


def fill_linkers(gapped, missing, output):
    """Use PDBFixer to add missing linker residues and atoms, then write the completed PDB."""
    fixer = PDBFixer(filename=str(gapped))
    fixer.missingResidues = missing
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    with output.open("w") as handle:
        PDBFile.writeFile(fixer.topology, fixer.positions, handle, keepIds=True)


def select_chains(source, output, keep):
    """Write a PDB containing only the requested source chains."""
    model = PDBParser(QUIET=True).get_structure(source.stem, source)[0]
    structure = Structure.Structure(output.stem)
    new_model = Model.Model(0)
    structure.add(new_model)
    for chain_id in keep:
        new_model.add(deepcopy(model[chain_id]))
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output))


def clash_metrics(path):
    """Measure inter-chain heavy-atom distances and count close contacts."""
    model = PDBParser(QUIET=True).get_structure(path.stem, path)[0]
    chains = list(model)
    values = []
    for i, first in enumerate(chains):
        xyz1 = atom_coords([protein_residues(first)])
        tree = cKDTree(xyz1)
        for second in chains[i + 1 :]:
            xyz2 = atom_coords([protein_residues(second)])
            distances, _ = tree.query(xyz2, k=1)
            values.append((first.id, second.id, float(distances.min()), int(np.sum(distances < 2.0))))
    return values


def build_construct(name, spec):
    """Build each configured state for one construct and write coordinates and metadata."""
    arm1, target1 = load_arm(spec.arm1)
    arm2, target2 = load_arm(spec.arm2)
    relationship = TARGET_RELATIONSHIPS[name]
    a1, t1, a2, t2, separation, theta, phi, connector, pre_min = place_complexes(
        arm1, target1, arm2, target2, relationship
    )
    parts = a1 + a2
    linkers = []
    for i in range(len(parts) - 1):
        boundary = i + 1
        linkers.append(ARM_LINKER if boundary == len(a1) else SCFV_LINKER)

    model_dir = spec.output / "models" / name
    assembly_dir = spec.output / "assemblies" / name
    analysis_dir = spec.output / "analysis" / name
    for directory in (model_dir, assembly_dir, analysis_dir):
        directory.mkdir(parents=True, exist_ok=True)
    gapped = model_dir / f"{name}_gapped_template.pdb"
    dual = assembly_dir / f"{name}_03_dual_bound.pdb"
    missing = write_gapped_with_plan(parts, linkers, t1, t2, gapped)
    fill_linkers(gapped, missing, dual)
    select_chains(dual, assembly_dir / f"{name}_00_unbound.pdb", ["A"])
    select_chains(dual, assembly_dir / f"{name}_01_{spec.arm1.target_name}_bound.pdb", ["A", "X"])
    select_chains(dual, assembly_dir / f"{name}_02_{spec.arm2.target_name}_bound.pdb", ["A", "Y"])

    rows = clash_metrics(dual)
    with (analysis_dir / "geometry_metrics.tsv").open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["metric", "value"])
        writer.writerow(["target_membrane_relationship", relationship])
        writer.writerow(["rigid_body_anchor_separation_A", separation])
        writer.writerow(["arm2_rotation_deg", theta])
        writer.writerow(["linker_azimuth_deg", phi])
        writer.writerow(["inter_arm_connector_distance_A", f"{connector:.3f}"])
        writer.writerow(["pre_linker_cross_body_min_distance_A", f"{pre_min:.3f}"])
        for first, second, minimum, clashes in rows:
            writer.writerow([f"post_build_min_distance_{first}_{second}_A", f"{minimum:.3f}"])
            writer.writerow([f"post_build_sub2A_atoms_{first}_{second}", clashes])

    (analysis_dir / "BUILD_PROVENANCE.md").write_text(
        f"# {name} assembly provenance\n\n"
        f"- Arm 1: `{spec.arm1.source.relative_to(ROOT)}`; target `{spec.arm1.target_name}` chain `{spec.arm1.target_chain}`.\n"
        f"- Arm 2: `{spec.arm2.source.relative_to(ROOT)}`; target `{spec.arm2.target_name}` chain `{spec.arm2.target_chain}`.\n"
        "- Variable-domain coordinates and source interfaces were preserved as rigid bodies. HuCL47–IL13Rα2 is predicted; other arm-target templates are experimental.\n"
        "- Internal scFv linkers: `(GGGGS)3` (15 residues).\n"
        "- Inter-arm linker: `(GGGGS)4` (20 residues).\n"
        f"- Sampled fragment-endpoint placement: {separation} A endpoint separation; connector distance {connector:.3f} A before linker building. These are not actual membrane anchors.\n"
        f"- Target membrane relationship modeled as `{relationship}` (trans = opposing cell surfaces; cis = same cell surface).\n"
        "- PDBFixer built linker coordinates and missing heavy atoms. No energy minimization or molecular dynamics was run.\n"
        "- These are starting hypotheses for geometry review. Flexible-linker placement and membrane spacing remain uncertain.\n"
    )
    return dual


def main():
    """Parse construct selections and run the configured structural assembly workflow."""
    parser = argparse.ArgumentParser()
    parser.add_argument("constructs", nargs="*", choices=sorted(CONFIGS), default=sorted(CONFIGS))
    args = parser.parse_args()
    for name in args.constructs:
        print(build_construct(name, CONFIGS[name]))


if __name__ == "__main__":
    main()
