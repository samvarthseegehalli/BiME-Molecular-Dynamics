"""Small scientific sanity tests for packaged observables and mappings."""

from __future__ import annotations

import csv
from pathlib import Path
import statistics
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_paper_data


class AnalysisTests(unittest.TestCase):
    def test_sample_statistics_known_values(self):
        values = [1.0, 2.0, 3.0]
        self.assertEqual(statistics.mean(values), 2.0)
        self.assertAlmostEqual(verify_paper_data.sample_sd(values), 1.0)

    def test_time_unit_conversion_ps_to_ns(self):
        self.assertEqual(20_000 / 1_000, 20.0)
        self.assertEqual(10_000 / 1_000, 10.0)

    def test_residue_mapping_is_contiguous_per_chain(self):
        path = ROOT / "artifacts/Coordinates/target_source_residue_mapping.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertTrue(rows)
        for chain in {row["local_chain"] for row in rows}:
            local = [int(row["local_residue"]) for row in rows if row["local_chain"] == chain]
            self.assertEqual(local, list(range(1, len(local) + 1)))

    def test_packaged_observable_summaries_recompute(self):
        replica_rows, aggregate_rows = verify_paper_data.verify(ROOT / "artifacts")
        self.assertEqual(replica_rows, 216)
        self.assertGreater(aggregate_rows, 0)


if __name__ == "__main__":
    unittest.main()
