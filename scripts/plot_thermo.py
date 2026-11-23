#!/usr/bin/env python3
"""Plot archived per-replica thermodynamic means as a portable SVG."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import statistics
import xml.sax.saxutils as xml

from verify_paper_data import DEFAULT_DATA_DIR


METRICS = (("Temperature", "Temperature (K)"),
           ("Pressure", "Pressure (bar)"),
           ("Density", "Density (kg/m³)"))
STATES = ("00_unbound", "01_egfrviii_bound", "02_sirpa_bound", "03_dual_bound")
COLORS = ("#0072B2", "#D55E00", "#009E73")


def render(data_dir: Path) -> str:
    """Render mean ± time SD for each replica in three independently scaled panels."""
    path = data_dir / "Analysis_Tables" / "manuscript_tables" / "thermodynamic_replica_summary.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    width, height = 980, 560
    panel_x = (130, 400, 670)
    labels = ("Unbound", "EGFRvIII bound", "SIRPα bound", "Dual bound")
    output = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<text x="490" y="28" text-anchor="middle" font-family="sans-serif" font-size="18">Archived thermodynamic replica summaries</text>']
    for panel, (metric, axis_label) in enumerate(METRICS):
        values = [float(row["mean"]) for row in records if row["metric"] == metric]
        low = min(values); high = max(values)
        margin = max((high - low) * 0.22, 0.01)
        y0, y1 = low - margin, high + margin
        x0 = panel_x[panel]
        output.extend([f'<text x="{x0+100}" y="66" text-anchor="middle" font-family="sans-serif" font-size="14">{xml.escape(axis_label)}</text>',
                       f'<line x1="{x0}" y1="105" x2="{x0}" y2="400" stroke="#333"/>'])
        for state_i, state in enumerate(STATES):
            x = x0 + 20 + state_i * 52
            output.append(f'<text x="{x}" y="420" text-anchor="middle" font-family="sans-serif" font-size="9">{labels[state_i]}</text>')
            rows = [r for r in records if r["metric"] == metric and r["state"] == state]
            for rep_i, row in enumerate(rows):
                mean = float(row["mean"]); sd = float(row["sd_time"])
                y = 400 - (mean - y0) / (y1 - y0) * 280
                err = sd / (y1 - y0) * 280
                xx = x + (rep_i - 1) * 10
                output.extend([f'<line x1="{xx}" y1="{y-err:.1f}" x2="{xx}" y2="{y+err:.1f}" stroke="{COLORS[rep_i]}"/>',
                               f'<circle cx="{xx}" cy="{y:.1f}" r="3.5" fill="{COLORS[rep_i]}"/>'])
        output.extend([f'<text x="{x0+100}" y="450" text-anchor="middle" font-family="sans-serif" font-size="9">State</text>',
                       f'<text x="{x0+100}" y="485" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Points: replicas; bars: within-run time SD</text>'])
    output.append('<text x="490" y="535" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">Descriptive simulation summaries; not convergence tests or experimental replicates.</text>')
    output.append('</svg>')
    return "\n".join(output) + "\n"


def main() -> int:
    """Write the portable thermodynamic summary figure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=Path("results/figures/thermodynamic_summary.svg"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.data_dir.resolve()), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
