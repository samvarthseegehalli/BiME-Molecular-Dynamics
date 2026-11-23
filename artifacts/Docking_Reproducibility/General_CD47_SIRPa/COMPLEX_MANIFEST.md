# Track A complex gate

The PDB files in this directory are immutable working copies of specific HDOCK poses. The original complete result bundles remain under `../docking/<run-id>/hdock-results/`.

## Accepted for structural and PRODIGY screening

| Run | Complex | Selected model | Recovery evidence | File | SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| A-RD-002 | B6H12.2–CD47 | 1 | LRMSD 0.330 Å; Fnat 1.0000 | `accepted/A-RD-002_B6H12.2_CD47_rank001.pdb` | `21a8fa8badeb8e434466bf1f2e77e0e1ddbda88a58d661c6d13e1c2079f59c4f` |
| A-RD-003 | C47B161–CD47 | 88 | LRMSD 3.282 Å; Fnat 0.9412; 32/34 native contacts recovered; experimental CDR interface reproduced | `accepted/A-RD-003_C47B161_CD47_rank088.pdb` | `584fb883fa89d80edc36b5ca9d157da1f8834c39791317bc89a69ff75e70f5a6` |
| A-RD-004 | C47B222–CD47 | 1 | LRMSD 1.664 Å; Fnat 0.9811 | `accepted/A-RD-004_C47B222_CD47_rank001.pdb` | `249147d3c42479efbc63f8fbf425494cfa7e01a38c3bfff54ddfc91afec916f8` |
| A-RD-005 | KWAR23–SIRPα | 1 | LRMSD 1.845 Å; Fnat 1.0000 | `accepted/A-RD-005_KWAR23_SIRPa_rank001.pdb` | `81bd856dae4bbc1485a50e1b4881a21f098fbe89dc466fce01f38205c7e63ebb` |
| A-RD-006 | Clone 119–SIRPα | 1 | LRMSD 1.524 Å; Fnat 0.9390 | `accepted/A-RD-006_clone119_SIRPa_rank001.pdb` | `d797f05b027b5cbfd5153f32154515cd0830c943c06509f7594437ddff3702c1` |
| A-RD-007 | Clone 136–SIRPα | 1 | LRMSD 0.332 Å; Fnat 0.9818 | `accepted/A-RD-007_clone136_SIRPa_rank001.pdb` | `4086f73011e5ed344afbf62b1d5ecfeef7f49622c39b323c803eaa0bdcdfa4e0` |
| A-RD-008 | Clone 115–SIRPα | 1 | LRMSD 1.042 Å; Fnat 0.9828 | `accepted/A-RD-008_clone115_SIRPa_rank001.pdb` | `e98dde8176b4476e11e75d0ea81579954080c2acec18f89df46a4064efd5385c` |
| A-RD-010 | 5F9–CD47, interface restrained | 4 | LRMSD 3.843 Å; Fnat 0.9524; 20/21 native contacts; epitope recall 1.0000; no sub-2.0 Å clash | `accepted/A-RD-010_5F9_CD47_rank004_restrained.pdb` | `4289268e41dac46aff5d6fa31624b3305b3b46b5863d83235e23722df9837c0b` |

## On hold for manual pose review

No complexes are currently on hold. C47B161 was promoted after reproducing the experimental CDR interface and passing the clash and epitope checks. Its rank-88 position remains a documented HDOCK ranking failure.

## Structural control

| Run | Complex | Selected model | Purpose | File | SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| A-RD-009 | Nonblocking clone 3–SIRPα | 6 | Binding but nonblocking comparator; do not rank as an inhibitor lead. | `controls/A-RD-009_clone3_nonblocking_SIRPa_rank006.pdb` | `681429ed22683af24f4da211a321473799e46b41b9af2dcd32947066f0348eba` |

## Resolved redocking failure

| Run | Complex | Status | Diagnostic file | SHA-256 |
| --- | --- | --- | --- | --- |
| A-RD-001 | 5F9–CD47 | Original unconstrained run recovered no native contacts. Retained as a diagnostic failure; replacement A-RD-010 succeeded. | `redock-required/A-RD-001_5F9_CD47_failed_rank001_diagnostic.pdb` | `2b6a744f7e18e4e41a41349e6d1bea03221026fea669fc3f6bea2664f130ad4c` |

The replacement job A-RD-010, [HDOCK 6ab2c07455d36](http://hdock.phys.hust.edu.cn/data/6ab2c07455d36/), used template-free docking with experimental binding-site residues `1-3:C, 27:C, 29:C, 100:C, 102-105:C` on CD47 and `28:B, 31-33:B, 52:B, 99-105:B` on 5F9. Rank 4 passed the recovery gate and is now in `accepted/`.

PRODIGY values are computational estimates for comparative screening. They are not experimental binding affinities and cannot override known blocking status or experimental measurements.
