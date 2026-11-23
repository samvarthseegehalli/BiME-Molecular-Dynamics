# HDOCK redocking controls

These jobs test whether template-free HDOCK can recover experimentally observed interfaces for glioblastoma-associated targeting arms. The antigen is entered as receptor and the antibody as ligand. These are protocol controls, not evidence that the target is unique to glioblastoma.

| Run ID | Antibody | Target | Experimental PDB | HDOCK receptor | HDOCK ligand | Mode | Status | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B-RD-001 | mAb806 | EGFR cryptic epitope peptide | 3G5V | `3G5V:AB` | `3G5V:C` | Template-free | Complete: rank-1 recovery | [6ab285204ce83](http://hdock.phys.hust.edu.cn/data/6ab285204ce83/) |
| B-RD-002 | Cetuximab Fab | EGFR extracellular domain | 1YY9 | `1YY9:A` | `1YY9:CD` | Template-free | Complete: rank-1 recovery | [6ab28565b7d57](http://hdock.phys.hust.edu.cn/data/6ab28565b7d57/) |
| B-RD-003 | Trastuzumab Fab | HER2 extracellular domain | 1N8Z | `1N8Z:C` | `1N8Z:AB` | Template-free | Complete: native-like rank 2 | [6ab286016a4bc](http://hdock.phys.hust.edu.cn/data/6ab286016a4bc/) |

## Audited but not submitted

| Antibody | Target | PDB | Reason |
| --- | --- | --- | --- |
| 8H9 | B7-H3/CD276 | 5CMA | The entry contains the Fab only and therefore cannot serve as an antibody–antigen redocking control. It remains eligible for later epitope-guided docking once a compatible B7-H3 structure and the experimental epitope constraints are prepared. |

## Source-file checksums

| PDB | SHA-256 |
| --- | --- |
| 3G5V | `3f726de377e0faf943e484cdf65461e149943bc7410625410c1a494455de2460` |
| 5CMA | `b435b7e45a0a6625622f6e7e8cfa0bbe50e7ff7e0531dccaf8981c55b4aab1c3` |
| 1YY9 | `e574b33a287c4100ff35f8346a6eadba1486d4a90464f4344f3189115f6d5fa8` |
| 1N8Z | `ed934d36503335c6764b08880f9e50933d99eb13b9bf145339cfcaee150eb21e` |

## Acceptance gate

For each completed job, align the receptor to the experimental complex and measure interface RMSD, ligand RMSD, fraction of native contacts and epitope overlap. Inspect whether antibody CDRs form the recovered interface and whether the pose is compatible with membrane presentation. Do not interpret a favorable HDOCK score as experimental affinity.

See [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) for measured recovery and the resulting protocol decision.
