#!/usr/bin/env python3
"""Generate a portable SVG interface-trace figure from the packaged XVG data."""

from __future__ import annotations

import argparse
from pathlib import Path
import statistics
import xml.sax.saxutils as xml

from verify_paper_data import DEFAULT_DATA_DIR, read_xvg


REPLICAS = ("replica-01", "replica-02", "replica-03")
SERIES = (("01_egfrviii_bound", "X", "EGFRvIII, single", "#0072B2"),
          ("02_sirpa_bound", "Y", "SIRPα, single", "#D55E00"),
          ("03_dual_bound", "X", "EGFRvIII, dual", "#56B4E9"),
          ("03_dual_bound", "Y", "SIRPα, dual", "#CC79A7"))


def xvg_path(data_dir: Path, state: str, replica: str, metric: str) -> Path:
    """Resolve an archived XVG metric under one state and replica."""
    return data_dir / "MD_Reproducibility" / "systems" / state / replica / "analysis_from_0ns" / f"{metric}.xvg"


def svg_figure(data_dir: Path) -> str:
    """Build an SVG plot of the four manuscript interface-contact series."""
    width, height = 980, 560
    left, right, top, bottom = 85, 950, 55, 465
    xmax, ymax = 20.0, 2200.0
    colors = {replica: color for replica, color in zip(REPLICAS, ("#0072B2", "#D55E00", "#009E73"))}
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="490" y="28" text-anchor="middle" font-family="sans-serif" font-size="18">Interface atom-pair contacts</text>']
    for tick in range(0, 2201, 400):
        y = bottom - (tick / ymax) * (bottom - top)
        lines.extend([f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#dddddd"/>',
                      f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick}</text>'])
    for tick in range(0, 21, 5):
        x = left + (tick / xmax) * (right - left)
        lines.extend([f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#eeeeee"/>',
                      f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick}</text>'])
    lines.extend([f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333"/>',
                  f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333"/>',
                  f'<text x="{(left+right)/2}" y="{height-38}" text-anchor="middle" font-family="sans-serif" font-size="14">Production time (ns)</text>',
                  f'<text x="22" y="{(top+bottom)/2}" transform="rotate(-90 22 {(top+bottom)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">Atom pairs within 0.45 nm</text>'])
    for index, (state, site, label, color) in enumerate(SERIES):
        collected = []
        for replica in REPLICAS:
            rows = read_xvg(xvg_path(data_dir, state, replica, f"interface_{site}_atom_contacts"))
            collected.append(rows)
        n = min(map(len, collected))
        means = [statistics.mean(rows[i][1] for rows in collected) for i in range(n)]
        points = " ".join(f"{left + row[0]/1000/xmax*(right-left):.1f},{bottom - value/ymax*(bottom-top):.1f}" for row, value in zip(collected[0][:n], means))
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
        lx, ly = 110 + (index % 2) * 260, 505 + (index // 2) * 22
        lines.extend([f'<line x1="{lx}" y1="{ly-4}" x2="{lx+24}" y2="{ly-4}" stroke="{color}" stroke-width="3"/>',
                      f'<text x="{lx+31}" y="{ly}" font-family="sans-serif" font-size="13">{xml.escape(label)} (replica mean)</text>'])
    lines.extend(['<text x="490" y="548" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">Means across three trajectory traces at each saved time; time points are not independent replicates.</text>', '</svg>'])
    return "\n".join(lines) + "\n"


def main() -> int:
    """Write the reproducible interface plot from packaged XVG files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="artifact root containing MD_Reproducibility/")
    parser.add_argument("--output", type=Path, default=Path("results/figures/interface_contacts.svg"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg_figure(args.data_dir.resolve()), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
