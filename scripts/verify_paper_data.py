#!/usr/bin/env python3
"""Recompute manuscript scalar summaries from the packaged GROMACS XVG files.

Run from any working directory with ``python scripts/verify_paper_data.py``.
The default data root is this repository's ``artifacts`` directory; override it
with ``--data-dir`` when the artifact package is stored elsewhere.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import statistics
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPOSITORY_ROOT / "artifacts"


def read_xvg(path: Path) -> list[list[float]]:
    """Read numeric columns from a GROMACS XVG file, ignoring metadata lines."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "@")):
            continue
        rows.append([float(value) for value in stripped.split()])
    if not rows:
        raise ValueError(f"No numeric rows in {path}")
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    """Return CSV records using UTF-8 and newline-safe parsing."""
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sample_sd(values: list[float]) -> float:
    """Return sample standard deviation, requiring at least two observations."""
    if len(values) < 2:
        raise ValueError("Sample standard deviation requires at least two values")
    return statistics.stdev(values)


def close(actual: float, expected: float, *, atol: float = 1e-8) -> bool:
    """Compare floating-point values with a small absolute tolerance."""
    return math.isclose(actual, expected, rel_tol=1e-10, abs_tol=atol)


def verify(data_dir: Path) -> tuple[int, int]:
    """Recompute per-replica and aggregate rows from XVG observations."""
    md_root = data_dir / "MD_Reproducibility" / "systems"
    tables = data_dir / "Analysis_Tables" / "manuscript_tables"
    replica_records = read_csv(tables / "replica_metrics.csv")
    aggregate_records = read_csv(tables / "aggregate_metrics.csv")
    observed: dict[tuple[str, str, str, str], list[float]] = {}

    for record in replica_records:
        state, replica, metric, window = (record[key] for key in ("state", "replica", "metric", "window_ns"))
        series = md_root / state / replica / "analysis_from_0ns" / f"{metric}.xvg"
        rows = read_xvg(series)
        if any(len(row) <= int(record["column"]) for row in rows):
            raise ValueError(f"Column {record['column']} missing from {series}")
        if rows[0][0] != 0 or rows[-1][0] != 20000 or len(rows) != 2001:
            raise ValueError(f"Unexpected trajectory sampling in {series}")
        start_ps = 10_000 if window == "10-20" else 0
        selected = [row for row in rows if row[0] >= start_ps]
        values = [row[int(record["column"])] for row in selected]
        expected_mean = float(record["mean"])
        expected_sd = float(record["sd_time"])
        if len(values) != int(record["n_frames"]):
            raise AssertionError(f"Frame count mismatch: {series} ({window})")
        if not close(statistics.mean(values), expected_mean):
            raise AssertionError(f"Mean mismatch: {series} ({window})")
        if not close(sample_sd(values), expected_sd):
            raise AssertionError(f"Time SD mismatch: {series} ({window})")
        if "atom_contacts" in metric and min(values) <= 0:
            raise AssertionError(f"Expected persistent contacts: {series}")
        if "sasa" in metric and int(record["column"]) != 2:
            raise AssertionError(f"Unexpected SASA data column: {series}")
        observed.setdefault((state, metric, window, replica), []).append(expected_mean)

    for record in aggregate_records:
        key = (record["state"], record["metric"], record["window_ns"])
        values = [float(row["mean"]) for row in replica_records if tuple(row[k] for k in ("state", "metric", "window_ns")) == key]
        if len(values) != 3:
            raise AssertionError(f"Expected three replica means for {key}, found {len(values)}")
        if not close(statistics.mean(values), float(record["mean"])):
            raise AssertionError(f"Aggregate mean mismatch: {key}")
        if not close(sample_sd(values), float(record["between_replica_sd"])):
            raise AssertionError(f"Between-replica SD mismatch: {key}")

    return len(replica_records), len(aggregate_records)


def main(argv: list[str] | None = None) -> int:
    """Parse options and verify the published scalar summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="artifact root containing Analysis_Tables/ and MD_Reproducibility/")
    args = parser.parse_args(argv)
    try:
        replica_count, aggregate_count = verify(args.data_dir.resolve())
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    print(f"Verified {replica_count} replica metric rows and {aggregate_count} aggregate rows from packaged XVG data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
