#!/usr/bin/env python3
"""Verify package paths, byte sizes, and SHA-256 hashes against the inventory."""
import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "artifacts" / "PACKAGE_FILE_MANIFEST.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    args = parser.parse_args()
    manifest = args.root / "artifacts" / "PACKAGE_FILE_MANIFEST.csv"
    failures = []
    checked = 0
    with manifest.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            relative = Path(row["path"])
            if relative.is_absolute() or ".." in relative.parts:
                failures.append(f"unsafe inventory path: {relative}")
                continue
            path = args.root / "artifacts" / relative
            if not path.is_file():
                failures.append(f"missing: {relative}")
                continue
            checked += 1
            if path.stat().st_size != int(row["bytes"]):
                failures.append(f"size mismatch: {relative}")
                continue
            digest = hashlib.sha256()
            with path.open("rb") as data:
                for block in iter(lambda: data.read(1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest().lower() != row["sha256"].lower():
                failures.append(f"SHA-256 mismatch: {relative}")
    sums = args.root / "artifacts" / "PACKAGE_SHA256SUMS.txt"
    if sums.is_file():
        for line_number, line in enumerate(sums.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                expected, name = line.split(maxsplit=1)
            except ValueError:
                failures.append(f"malformed SHA256SUMS line {line_number}")
                continue
            relative = Path(name.lstrip("* "))
            if relative.is_absolute() or ".." in relative.parts:
                failures.append(f"unsafe SHA256SUMS path: {name}")
                continue
            path = args.root / "artifacts" / relative
            if not path.is_file():
                failures.append(f"SHA256SUMS file missing: {relative}")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest.lower() != expected.lower():
                failures.append(f"SHA256SUMS mismatch: {relative}")
    if failures:
        print(f"FAILED: {len(failures)} issue(s); checked {checked} files")
        print("\n".join(failures))
        return 1
    print(f"OK: verified {checked} inventoried files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
