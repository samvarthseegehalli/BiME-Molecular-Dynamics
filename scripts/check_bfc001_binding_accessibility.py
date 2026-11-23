#!/usr/bin/env python3
"""Sample B-FC-001 binding-face exposure and unwanted cross-arm contacts.

Paratope residues are defined from the starting dual-bound model as construct
residues within 4.5 Å of each experimental-template target. This is a geometric
proxy, not a formal antibody CDR or affinity assignment.
"""

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.spatial import cKDTree


STATES = ("00_unbound", "01_egfrviii_bound", "02_sirpa_bound", "03_dual_bound")


def pdb_atoms(path):
    atoms = {chain: [] for chain in "AXY"}
    for line in path.read_text().splitlines():
        if not line.startswith("ATOM") or line[21] not in atoms:
            continue
        element = line[76:78].strip().upper()
        if element in {"H", "D"} or line[12:16].strip().startswith("H"):
            continue
        atoms[line[21]].append((int(line[22:26]),
                                [float(line[i:i + 8]) for i in (30, 38, 46)]))
    return atoms


def paratope_residues(dual_pdb):
    atoms = pdb_atoms(dual_pdb)
    result = {}
    for target in "XY":
        tree = cKDTree(np.array([coord for _, coord in atoms[target]]))
        result[target] = sorted({res for res, coord in atoms["A"]
                                 if tree.query(coord)[0] <= 4.5})
    return result


def append_index(system, paratopes, output):
    gro_path = system / "processed.gro"
    if not gro_path.exists():
        gro_path = system / "em.gro"
    gro = gro_path.read_text().splitlines()
    construct_indices = set()
    current = None
    for line in (system / "analysis.ndx").read_text().splitlines():
        if line.startswith("["):
            current = line.strip("[] ")
        elif current == "Construct":
            construct_indices.update(map(int, line.split()))
    selections = {target: [] for target in "XY"}
    for line in gro[2:-1]:
        atom_id = int(line[15:20])
        if atom_id not in construct_indices:
            continue
        res = int(line[:5])
        for target, residues in paratopes.items():
            if res in residues:
                selections[target].append(atom_id)
    with output.open("w") as dst:
        dst.write((system / "analysis.ndx").read_text())
        for target, atom_ids in selections.items():
            dst.write(f"\n[ Paratope_{target} ]\n")
            for start in range(0, len(atom_ids), 15):
                dst.write(" ".join(map(str, atom_ids[start:start + 15])) + "\n")
    if any(not ids for ids in selections.values()):
        raise ValueError(f"Empty paratope index in {system}: {selections}")


def run_gmx(gmx, command, log, selection=""):
    with log.open("w") as output:
        subprocess.run([gmx] + command, input=selection, text=True,
                       stdout=output, stderr=subprocess.STDOUT, check=True)


def xvg_values(path):
    rows = []
    for line in path.read_text().splitlines():
        if line and line[0] not in "#@":
            try:
                rows.append([float(value) for value in line.split()])
            except ValueError:
                pass
    return np.asarray(rows)


def summary(path, column=1):
    rows = xvg_values(path)
    values = rows[:, column]
    return {"n_frames": int(len(values)), "mean": float(values.mean()),
            "min": float(values.min()), "max": float(values.max()),
            "first_half_mean": float(values[:len(values)//2].mean()),
            "second_half_mean": float(values[len(values)//2:].mean())}


def analyze_state(root, state, replica, paratopes, gmx, interval_ps):
    system = root / state
    run = system / replica
    trajectory = run / "analysis_from_0ns" / "protein_nojump.xtc"
    tpr = run / "md_20ns.tpr"
    if not trajectory.exists() or not tpr.exists():
        return None
    out = run / "binding_accessibility_500ps"
    out.mkdir(exist_ok=True)
    index = out / "paratopes.ndx"
    append_index(system, paratopes, index)
    common = ["-s", str(tpr), "-f", str(trajectory), "-n", str(index),
              "-dt", str(interval_ps)]
    metadata = {"state": state, "replica": replica, "interval_ps": interval_ps,
                "paratope_residues": paratopes, "metrics": {}}
    sites = "XY" if state == "00_unbound" else ("Y" if state == "01_egfrviii_bound" else ("X" if state == "02_sirpa_bound" else "XY"))
    for site in sites:
        for surface in ("Construct", "Protein") if state != "00_unbound" else ("Construct",):
            name = f"site_{site}_sasa_surface_{surface}_nm2"
            dest = out / f"{name}.xvg"
            run_gmx(gmx, ["sasa"] + common + ["-surface", f'group "{surface}"',
                     "-output", f'group "Paratope_{site}"', "-o", str(dest)],
                    out / f"{name}.log")
            metadata["metrics"][name] = summary(dest, column=2)
        opposing_arm = "Arm2" if site == "X" else "Arm1"
        for partner in (opposing_arm, "Linker1"):
            name = f"site_{site}_vs_{partner}"
            dist = out / f"{name}_minimum_nm.xvg"
            contacts = out / f"{name}_atom_contacts.xvg"
            run_gmx(gmx, ["mindist"] + common + ["-d", "0.45", "-od", str(dist),
                     "-on", str(contacts)], out / f"{name}.log",
                    f"Paratope_{site}\n{partner}\n")
            metadata["metrics"][name] = {"distance_nm": summary(dist),
                                          "atom_contacts": summary(contacts)}
        cross_target = "Target_Y" if site == "X" else "Target_X"
        if state == "01_egfrviii_bound" and site == "Y" or state == "02_sirpa_bound" and site == "X":
            name = f"site_{site}_vs_{cross_target}"
            dist = out / f"{name}_minimum_nm.xvg"
            contacts = out / f"{name}_atom_contacts.xvg"
            run_gmx(gmx, ["mindist"] + common + ["-d", "0.45", "-od", str(dist),
                     "-on", str(contacts)], out / f"{name}.log",
                    f"Paratope_{site}\n{cross_target}\n")
            metadata["metrics"][name] = {"distance_nm": summary(dist),
                                          "atom_contacts": summary(contacts)}
    (out / "summary.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--replica", required=True)
    parser.add_argument("--states", nargs="+", choices=STATES, default=STATES)
    parser.add_argument("--gmx", required=True)
    parser.add_argument("--interval-ps", type=int, default=500)
    parser.add_argument("--template-pdb", type=Path)
    args = parser.parse_args()
    dual_pdb = args.template_pdb or args.root / "03_dual_bound" / "input.pdb"
    paratopes = paratope_residues(dual_pdb)
    print(json.dumps({"paratope_residues": paratopes}), flush=True)
    for state in args.states:
        print(f"Analyzing {state} {args.replica}", flush=True)
        result = analyze_state(args.root, state, args.replica, paratopes,
                               args.gmx, args.interval_ps)
        print(json.dumps(result or {"state": state, "status": "no completed trajectory"}), flush=True)


if __name__ == "__main__":
    main()
