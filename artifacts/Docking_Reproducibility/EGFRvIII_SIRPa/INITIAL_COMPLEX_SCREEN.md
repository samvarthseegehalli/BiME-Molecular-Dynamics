# Track B initial complex screen

PRODIGY 2.4.0 was run locally at 25 °C on the exact PDB files listed in `../complexes/COMPLEX_MANIFEST.md`. These are computational estimates for comparative triage, not measured affinities.

| Run | Complex | Selected pose | PRODIGY ΔG (kcal/mol) | Predicted Kd (M) | PRODIGY contacts | Minimum interpartner distance (Å) | Atom clashes <2.0 Å |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B-RD-001 | mAb806–EGFR epitope peptide | 1 | -13.2 | 2.3e-10 | 67 | 2.374 | 0 |
| B-RD-002 | Cetuximab–EGFR | 1 | -10.7 | 1.5e-08 | 87 | 2.311 | 0 |
| B-RD-003 | Trastuzumab–HER2 | 2 | -10.4 | 2.5e-08 | 73 | 2.057 | 0 |
| B-EXP-001 | MR1 dsFv–EGFRvIII junction peptide (1I8K) | Experimental | -9.7 | 7.9e-08 | 55 | 2.690 | 0 |
| B-EXP-002 | VHH 34E5–EGFRvIII ectodomain (8UKV A/C) | Experimental | -10.7 | 1.5e-08 | 69 | 2.497 | 0 |
| B-DOCK-002 | 2173 Fv–EGFRvIII junction peptide | 3 | -10.1 | 4.2e-08 | 48 | 2.353 | 0 |
| B-DOCK-001 | HuCL47 Fv–IL13Rα2, global | 34 | -10.1 | 3.8e-08 | 67 | 2.322 | 0 |
| B-DOCK-003 | HuCL47 Fv–IL13Rα2, guided consensus | 44 | -10.4 | 2.2e-08 | 75 | 2.191 | 0 |

## Preliminary interpretation

- All five selected structures are free of interpartner atom contacts below 2.0 Å.
- The mAb806 value is not directly comparable with the two full ectodomain complexes because its antigen is a short crystallographic epitope peptide.
- The same peptide-versus-ectodomain limitation applies to MR1. Its crystallographic pose is strong evidence for neoepitope recognition, while its PRODIGY value should not be ranked directly against 34E5 on the full ectodomain.
- 34E5 is the strongest current Track B structural starting point: an experimentally solved EGFRvIII ectodomain complex with measured preferential binding to EGFRvIII over wild-type EGFR. Its reported selectivity is preferential rather than absolute.
- The 2173 pose passes the CDR-use, peptide-coverage and clash gates, but remains a predicted Fv–peptide pose. It does not solve the intact-receptor junction-accessibility problem.
- The two HuCL47 runs converge despite different restraint conditions. This is stronger evidence than either server score alone, but both share the same predicted Fv and receptor crystal structure and are therefore not statistically independent biological observations.
- Cetuximab and trastuzumab are workflow controls and structural comparators. Neither establishes glioblastoma selectivity.
- Selecting the eventual tumor-directed arm still requires target-prevalence evidence, epitope accessibility and membrane-aware geometry. Sequence-derived candidates such as 2173 and HuCL47 remain in model preparation and must stay distinct from experimentally solved complexes.

Raw PRODIGY reports and QC tables are in `prodigy/`.
