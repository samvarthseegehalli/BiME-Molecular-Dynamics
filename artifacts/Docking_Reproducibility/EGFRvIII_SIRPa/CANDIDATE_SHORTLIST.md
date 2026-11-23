# Track B tumor-directed arm shortlist

| Priority | Candidate / target | Current structural evidence | Decision |
| ---: | --- | --- | --- |
| 1 | VHH 34E5 / EGFRvIII | Experimental full-ectodomain complex PDB 8UKV; reported ~18-fold tighter SPR binding to EGFRvIII than wild-type EGFR | Advance as the best-supported current pose. Retain the qualification that selectivity is preferential rather than absolute. |
| 2 | MR1 / EGFRvIII junction | Experimental dsFv–junction-peptide complex PDB 1I8K | Advance as an EGFRvIII neoepitope arm; test junction accessibility in the intact/membrane context. |
| 3 | 2173 / EGFRvIII junction | Exact VH/VL provenance; ABodyBuilder2 Fv model; rank-3 junction-peptide pose passes CDR-use, peptide-coverage and clash gates | Advance to a peptide-complex MD screen. Treat it as a limited model because the junction is unresolved and flexible in available EGFRvIII ectodomain structures. |
| 4 | HuCL47 / IL13Rα2 | Exact VH/VL provenance; ABodyBuilder2 Fv; global rank 34 independently reproduced by guided rank 44 at 2.107 Å with Fnat 0.9583; all four experimental-site residues contacted; no clash | Advance to a short MD screen as a predicted consensus pose. The pose remains computational and requires experimental structure or mutational validation. |
| 5 | mAb806 / altered or amplified EGFR | Experimental peptide complex and successful redocking control | Retain as a GBM-associated comparator. It is not EGFRvIII-exclusive and should not be described as universally glioblastoma-specific. |
| Reserve | 8H9 / B7-H3 | Experimental Fv structure and mapped B7-H3 epitope, but no human antibody–antigen complex in the current workspace | Hold until a defensible human B7-H3 ectodomain model and membrane geometry are prepared. |

Cetuximab and trastuzumab remain workflow controls. They are not tumor-selective Track B leads.

## Immediate next gate

1. Run the prepared short MD screens for the accepted experimental and predicted systems on the GPU cluster.
2. Reject poses that do not use the antibody CDR surface or that conflict with the membrane-facing receptor geometry.
3. Keep the experimental 34E5 and MR1 complexes as reference poses rather than replacing them with lower-quality redocked geometries.
4. Prepare MD only after each candidate has an explicit antigen construct, antibody construct, protonation plan, glycan policy and pose provenance.
