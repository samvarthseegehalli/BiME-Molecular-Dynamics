# Track A candidate shortlist after redocking QC

## CD47-binding arms

| Priority | Candidate | Decision | Basis |
| ---: | --- | --- | --- |
| 1 | B6H12.2 | Advance | Blocking reference; rank-1 native-interface recovery; no clash; strongest accepted CD47 PRODIGY estimate. |
| 2 | Hu5F9-G4 / 5F9 | Advance | Therapeutic comparator with measured 8 nM monomeric-CD47 affinity. The unconstrained redock failed, but the experimentally restrained rerun recovered 20/21 native contacts at rank 4 with full epitope recall and no clash. |
| 3 | C47B161 | Advance | Blocking and experimentally antileukemic; recovered 32/34 native contacts after manual rank-88 review; no clash. |
| 4 | C47B222 | Advance | Blocking and experimentally active; rank-1 native-interface recovery; no clash. |

## SIRPα-binding arms

| Priority | Candidate | Decision | Basis |
| ---: | --- | --- | --- |
| 1 | KWAR23 | Advance | Blocking, public sequence and structure, common-allele evidence; rank-1 recovery; no clash; strongest SIRPα PRODIGY estimate. |
| 2 | Clone 119 | Advance | Blocking and pan-allelic discovery evidence; rank-1 recovery; largest contact count; no clash. |
| 3 | Clone 136 | Advance as diversity comparator | Distinct structurally solved blocking pose; excellent redocking recovery; no clash. |
| 4 | Clone 115 | Retain as mechanism comparator | Experimentally reported “kick-off” mechanism; recovered native pose; weaker preliminary PRODIGY estimate. |
| Control | Clone 3 | Do not use as an inhibitory arm | Experimentally binding but nonblocking. It remains the negative control demonstrating that binding score alone does not establish checkpoint inhibition. |

## Next gate

The next expensive step should use experimental complex coordinates for the advanced arms, with redocking retained as method validation. Before production MD, standardize protonation, missing atoms/residues, glycans, termini, disulfides and the exact construct boundaries. The candidate ranking must combine experimental blockade, allele coverage, epitope overlap and construct geometry; PRODIGY alone cannot select the final arm.
