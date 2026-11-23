#!/usr/bin/env python3
"""Build protein-only solvated GROMACS systems for every relaxed state."""

from __future__ import annotations

import csv
import subprocess
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("track-a-general-cd47-sirpa", "track-b-glioblastoma-targeted")


def main() -> None:
    runner = ROOT / "scripts/prepare_gromacs_system.sh"
    rows = []
    for track in TRACKS:
        base = ROOT / track / "constructs"
        for source in sorted((base / "assemblies").glob("*/*.pdb")):
            construct = source.stem.split("_", 1)[0]
            state = source.stem.split("_", 1)[1]
            relaxed = base / "models" / construct / "linker_relaxed_states" / f"{source.stem}_linker_relaxed.pdb"
            output = ROOT / track / "md/complete-constructs" / construct / state.lower()
            report_path = output / "SYSTEM_BUILD.log"
            if (output / 'em.tpr').is_file():
                raw = output / 'input_raw.pdb'
                if not raw.is_file() or raw.read_bytes() != relaxed.read_bytes():
                    # Preserve stale systems rather than silently pairing new PDBs with old TPRs.
                    archive = ROOT / track / 'md/archived-stale-inputs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') / construct / state.lower()
                    archive.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(output), str(archive))
                    print(f'Archived stale system: {archive.relative_to(ROOT)}', flush=True)
            output.mkdir(parents=True, exist_ok=True)
            if (output / "em.tpr").is_file():
                result_code, output_text = 0, "Existing em.tpr found; retained existing prepared system."
                if not report_path.exists():
                    report_path.write_text(output_text + "\n")
            else:
                result = subprocess.run(["bash", str(runner), str(relaxed), str(output)], cwd=ROOT, text=True, capture_output=True)
                result_code, output_text = result.returncode, result.stdout + result.stderr
                report_path.write_text(output_text)
            em_tpr = output / "em.tpr"
            water_log = output / "03_solvate.log"
            rows.append({
                "track": track,
                "construct": construct,
                "state": state,
                "exit_code": result_code,
                "em_tpr_exists": em_tpr.is_file(),
                "em_tpr_bytes": em_tpr.stat().st_size if em_tpr.exists() else 0,
                "water_log": str(water_log.relative_to(ROOT)),
                "build_log": str(report_path.relative_to(ROOT)),
                "system_dir": str(output.relative_to(ROOT)),
            })
            print(f"{construct}/{state}: exit={result_code} em.tpr={em_tpr.is_file()}", flush=True)
    report = ROOT / "complete_construct_system_build.tsv"
    with report.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if row["exit_code"] or not row["em_tpr_exists"]]
    print(f"states={len(rows)} failures={len(failures)} report={report}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
