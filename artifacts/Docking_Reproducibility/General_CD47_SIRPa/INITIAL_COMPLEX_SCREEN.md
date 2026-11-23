# Track A initial complex screen

PRODIGY 2.4.0 was run locally at 25 °C on the exact PDB files listed in `../complexes/COMPLEX_MANIFEST.md`. The structural screen counts heavy-atom contacts between the antigen and antibody chain groups. These values are computational estimates for comparative triage, not measured affinities.

| Run | Complex | Gate | Selected pose | PRODIGY ΔG (kcal/mol) | Predicted Kd (M) | PRODIGY contacts | Minimum interpartner distance (Å) | Atom clashes <2.0 Å |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A-RD-002 | B6H12.2–CD47 | Accepted | 1 | -13.5 | 1.3e-10 | 102 | 2.284 | 0 |
| A-RD-003 | C47B161–CD47 | Accepted after manual review | 88 | -12.4 | 8.1e-10 | 65 | 2.299 | 0 |
| A-RD-004 | C47B222–CD47 | Accepted | 1 | -11.2 | 6.3e-09 | 68 | 2.339 | 0 |
| A-RD-005 | KWAR23–SIRPα | Accepted | 1 | -13.6 | 1.0e-10 | 91 | 2.234 | 0 |
| A-RD-006 | Clone 119–SIRPα | Accepted | 1 | -11.8 | 2.2e-09 | 111 | 2.149 | 0 |
| A-RD-007 | Clone 136–SIRPα | Accepted | 1 | -11.1 | 7.3e-09 | 69 | 2.205 | 0 |
| A-RD-008 | Clone 115–SIRPα | Accepted | 1 | -10.7 | 1.5e-08 | 79 | 2.200 | 0 |
| A-RD-009 | Nonblocking clone 3–SIRPα | Control | 6 | -10.2 | 3.4e-08 | 72 | 1.667 | 1 |
| A-RD-010 | 5F9–CD47, interface restrained | Accepted | 4 | -9.6 | 8.6e-08 | 40 | 2.290 | 0 |

## Preliminary interpretation

- B6H12.2 and KWAR23 have the strongest PRODIGY estimates among currently accepted CD47 and SIRPα complexes, respectively.
- Clone 119 has the largest reported contact count, but its predicted ΔG is weaker than KWAR23. Contact count alone does not define affinity or blocking activity.
- C47B161 was promoted after manual review: it recovers 32 of 34 native contacts, reproduces 91% of the experimental CD47 epitope, uses the experimental heavy- and light-chain CDR interface, and has no sub-2.0 Å clash. Its rank-88 placement remains evidence that HDOCK score alone is an unreliable selector.
- The nonblocking clone 3 binds with a plausible interface despite being a functional nonblocker. This confirms that predicted affinity cannot substitute for checkpoint-obstruction evidence.
- The interface-restrained 5F9 run recovered the experimental surface at rank 4 without clashes. Its weaker PRODIGY estimate does not override the measured 8 nM monomeric-CD47 affinity or its extensive experimental evidence; it illustrates the limited comparability of this empirical score across constructs and poses.

Raw PRODIGY reports and QC tables are in `prodigy/`.
