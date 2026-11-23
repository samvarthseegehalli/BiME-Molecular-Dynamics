# Track A redocking validation

## Current results

The measurements below align the receptor in each HDOCK model to the experimental receptor and then compare the docked ligand with its experimental pose. `Fnat` is the fraction of experimental residue–residue contacts recovered at a 5 Å heavy-atom cutoff. HDOCK's displayed RMSD is the displacement from the initial ligand orientation and is not used as an accuracy measure.

| Run | System | Rank-1 ligand RMSD (Å) | Rank-1 Fnat | Best native-like model in top 100 | Interpretation |
| --- | --- | ---: | ---: | --- | --- |
| A-RD-001 | 5F9–CD47 | 78.535 | 0.0000 | Rank 68: 49.323 Å, Fnat 0.0000 | Sampling failure; rerun with experimental epitope/interface restraints. |
| A-RD-002 | B6H12.2–CD47 | 0.330 | 1.0000 | Rank 1 | Pass: native interface recovered and ranked first. |
| A-RD-003 | C47B161–CD47 | 48.316 | 0.0588 | Rank 88: 3.282 Å, Fnat 0.9412 | Sampling pass, ranking failure; keep a broad ensemble and rerank with epitope evidence. |
| A-RD-004 | C47B222–CD47 | 1.664 | 0.9811 | Rank 1 | Pass: near-native interface recovered and ranked first. |
| A-RD-005 | KWAR23–SIRPα | 1.845 | 1.0000 | Rank 1 | Pass: near-native interface recovered and ranked first. |
| A-RD-006 | Clone 119–SIRPα | 1.524 | 0.9390 | Rank 1 | Pass: near-native interface recovered and ranked first. |
| A-RD-007 | Clone 136–SIRPα | 0.332 | 0.9818 | Rank 1 | Pass: near-native interface recovered and ranked first. |
| A-RD-008 | Clone 115–SIRPα | 1.042 | 0.9828 | Rank 1 | Pass: near-native interface recovered and ranked first. |
| A-RD-009 | Nonblocking clone 3–SIRPα | 53.438 | 0.0000 | Rank 6: 5.986 Å, Fnat 0.9592 | Sampling pass, ranking failure; useful nonblocking geometry comparator. |
| A-RD-010 | 5F9–CD47, interface restrained | 11.756 | 0.8571 | Rank 4: 3.843 Å, Fnat 0.9524, epitope recall 1.0000 | Restrained rescue succeeds. Rank 4 is retained because it recovers 20/21 native contacts and the full experimental epitope. |

## Protocol decision

Unconstrained HDOCK can recover several known checkpoint interfaces, but the original 5F9 failure and C47B161 rank-88 result show that the top server score cannot be used alone. The restrained 5F9 rescue demonstrates that experimentally justified interface information can recover the correct contact surface, although the best contact-recovery pose was server rank 4. Unresolved candidates will use experimental epitope restraints where available, retain the top 100 models, cluster by interface, and rerank by epitope recovery, CDR involvement, clashes, membrane geometry and checkpoint-interface obstruction before MD.

The complete server bundles and per-model metrics are stored under each `A-RD-*` directory. The metrics were generated with [`../../scripts/validate_redocking.py`](../../scripts/validate_redocking.py).
