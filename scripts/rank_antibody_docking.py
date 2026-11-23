#!/usr/bin/env python3
"""Rank antibody docking poses by CDR use, antigen coverage, score and clashes."""

from __future__ import annotations

import argparse
import csv
import glob
import math
import re
from pathlib import Path


def parse_ranges(text: str) -> dict[str, list[tuple[int, int]]]:
    out: dict[str, list[tuple[int, int]]] = {}
    for item in text.split(","):
        span, chain = item.strip().split(":")
        if "-" in span:
            left, right = map(int, span.split("-"))
        else:
            left = right = int(span)
        out.setdefault(chain, []).append((left, right))
    return out


def in_ranges(chain: str, resseq: int, ranges: dict[str, list[tuple[int, int]]]) -> bool:
    return any(left <= resseq <= right for left, right in ranges.get(chain, []))


def parse_pdb(path: Path):
    score = math.nan
    atoms = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("REMARK Score:"):
            score = float(line.split()[-1])
        if not line.startswith(("ATOM  ", "HETATM")) or len(line) < 54:
            continue
        try:
            xyz = tuple(float(line[i:j]) for i, j in ((30, 38), (38, 46), (46, 54)))
            resseq = int(line[22:26])
        except ValueError:
            continue
        atoms.append((line[21:22], resseq, line[26:27].strip(), line[12:16].strip(), xyz))
    return score, atoms


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--models-dir", type=Path, required=True)
    p.add_argument("--antibody-chains", required=True)
    p.add_argument("--antigen-chains", required=True)
    p.add_argument("--cdr-ranges", required=True)
    p.add_argument("--antigen-site", default="", help="Optional chain-aware residue ranges used as experimental support")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    antibody_chains = set(args.antibody_chains.replace(",", ""))
    antigen_chains = set(args.antigen_chains.replace(",", ""))
    cdr_ranges = parse_ranges(args.cdr_ranges)
    antigen_site = parse_ranges(args.antigen_site) if args.antigen_site else {}

    rows = []
    for name in glob.glob(str(args.models_dir / "model_*.pdb")):
        path = Path(name)
        match = re.search(r"model_(\d+)\.pdb$", path.name)
        if not match:
            continue
        rank = int(match.group(1))
        score, atoms = parse_pdb(path)
        ab = [a for a in atoms if a[0] in antibody_chains]
        ag = [a for a in atoms if a[0] in antigen_chains]
        ab_contacts = set()
        ag_contacts = set()
        min_distance = math.inf
        clashes = 0
        for a in ab:
            for b in ag:
                d = math.dist(a[4], b[4])
                min_distance = min(min_distance, d)
                if d < 2.0:
                    clashes += 1
                if d <= 5.0:
                    ab_contacts.add((a[0], a[1], a[2]))
                    ag_contacts.add((b[0], b[1], b[2]))
        cdr_contacts = {r for r in ab_contacts if in_ranges(r[0], r[1], cdr_ranges)}
        cdr_fraction = len(cdr_contacts) / len(ab_contacts) if ab_contacts else 0.0
        all_ag_res = {(a[0], a[1], a[2]) for a in ag}
        site_res = {r for r in all_ag_res if in_ranges(r[0], r[1], antigen_site)}
        site_contacts = site_res & ag_contacts
        ag_coverage = len(ag_contacts) / len(all_ag_res) if all_ag_res else 0.0
        rows.append(
            {
                "rank": rank,
                "score": score,
                "minimum_distance_A": min_distance,
                "atom_clashes_lt_2A": clashes,
                "antibody_contact_residues": len(ab_contacts),
                "cdr_contact_residues": len(cdr_contacts),
                "cdr_contact_fraction": cdr_fraction,
                "antigen_contact_residues": len(ag_contacts),
                "antigen_residue_coverage": ag_coverage,
                "experimental_site_residues_present": len(site_res),
                "experimental_site_residues_contacted": len(site_contacts),
                "experimental_site_contact_fraction": len(site_contacts) / len(site_res) if site_res else 0.0,
                "contact_fingerprint": ",".join(f"{c}:{r}{i}" for c, r, i in sorted(ab_contacts)),
                "model": path.name,
            }
        )
    rows.sort(key=lambda row: row["rank"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
