#!/usr/bin/env python3
"""Confirm every prepared complete-construct TPR can be read by GROMACS."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "complete_construct_system_build.tsv"
    rows = list(csv.DictReader(source.open(), delimiter="\t"))
    for row in rows:
        tpr = ROOT / row["system_dir"] / "em.tpr"
        result = subprocess.run(["gmx", "dump", "-s", str(tpr)], cwd=ROOT, text=True, capture_output=True)
        match = re.search(r"\bnatoms\s*=\s*(\d+)", result.stdout + result.stderr)
        row["tpr_readable"] = result.returncode == 0 and match is not None
        row["total_atoms"] = match.group(1) if match else ""
        row["verification_error"] = result.stderr[-500:].replace("\n", " ") if result.returncode else ""
        print(f"{row['construct']}/{row['state']}: readable={row['tpr_readable']} atoms={row['total_atoms']}", flush=True)
    report = ROOT / "complete_construct_system_build.tsv"
    fields = list(rows[0])
    with report.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if not row["tpr_readable"]]
    print(f"systems={len(rows)} unreadable={len(failures)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
