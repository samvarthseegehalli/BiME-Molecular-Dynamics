# Track B redocking validation

## Current results

| Run | System | Rank-1 ligand RMSD (Å) | Rank-1 Fnat | Interpretation |
| --- | --- | ---: | ---: | --- |
| B-RD-001 | mAb806–EGFR cryptic epitope peptide | 0.463 | 1.0000 | Pass: all 48 native residue contacts recovered at rank 1. This peptide control is structurally simpler than docking a full extracellular domain. |
| B-RD-002 | Cetuximab–EGFR | 0.676 | 1.0000 | Pass: all native residue contacts recovered at rank 1. |
| B-RD-003 | Trastuzumab–HER2 | 63.885 | 0.0000 | Ranking miss at rank 1; rank 2 is native-like at 0.874 Å ligand RMSD and Fnat 0.9787. |

The measurements align the receptor to the experimental structure before calculating ligand RMSD. `Fnat` is the fraction of experimental residue–residue contacts recovered at a 5 Å heavy-atom cutoff. The server bundle and all 100 per-model measurements for B-RD-001 are stored in its run directory.

All three controls sampled their experimental interfaces in the top two ranks. The mAb806 result validates recovery of its experimentally observed epitope-peptide geometry, but it does not establish glioblastoma selectivity or whole-EGFR accessibility. Those claims require separate expression/selectivity evidence and full-domain or membrane-aware modeling.
