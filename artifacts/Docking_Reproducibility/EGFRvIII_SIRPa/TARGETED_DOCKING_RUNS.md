# Track B targeted docking runs

## Completed runs

| Run | Candidate | Receptor | Ligand | Protocol | HDOCK job |
| --- | --- | --- | --- | --- | --- |
| B-DOCK-001 | HuCL47–IL13Rα2 | IL13Rα2 chain C from experimental PDB 3LB6 | ABodyBuilder2 HuCL47 Fv | Complete. Template-free global docking. Rank 34 retained: score -207.79; all four experimentally tested receptor residues contacted; 14/25 antibody contact residues within broad CDR ranges; no sub-2.0 Å clash. | [6ab2c8f94a32c](http://hdock.phys.hust.edu.cn/data/6ab2c8f94a32c/) |
| B-DOCK-002 | 2173–EGFRvIII junction | ABodyBuilder2 2173 Fv | EGFRvIII junction peptide, chain C from experimental PDB 1I8K | Complete. Template-free docking with broad IMGT CDR ranges on H/L and all resolved junction-peptide residues 499–510:C. Rank 3 retained: score -141.28; 9/10 peptide residues contacted; 16/18 antibody contact residues within the broad CDR ranges; no sub-2.0 Å clash. | [6ab2c9359b998](http://hdock.phys.hust.edu.cn/data/6ab2c9359b998/) |
| B-DOCK-003 | HuCL47–IL13Rα2, epitope-guided | IL13Rα2 chain C from experimental PDB 3LB6 | ABodyBuilder2 HuCL47 Fv | Complete. Template-free docking restrained to IL13Rα2 Tyr207, Asp271, Tyr315 and Asp318 plus broad CDR ranges. Rank 44 independently converges on global rank 34: ligand RMSD 2.107 Å after receptor alignment; 46/48 global-pose contacts recovered (Fnat 0.9583); no sub-2.0 Å clash. | [6ab2d017762b0](http://hdock.phys.hust.edu.cn/data/6ab2d017762b0/) |

## Interpretation rules

- B-DOCK-001 remains hypothesis-generating because the HuCL47 structure and complex pose are computational. Its primary rank-34 pose overlaps 11/25 IL-13-contacting receptor residues, including Tyr207, Tyr315 and Asp318, and covers 44% of the crystallographic IL-13 receptor interface.
- B-DOCK-003 provides the experimentally guided counterpart. Its independent convergence with the global pose supports a reproducible interface hypothesis; it does not turn the predicted complex into an experimental structure.
- B-DOCK-002 tests whether the modeled 2173 paratope can accommodate the experimentally defined EGFRvIII junction peptide. It does not model the unresolved junction in the intact ectodomain.
- PDB 8UKW cannot support a junction-directed 2173 dock by itself: residues 268–304 are present in SEQRES but absent from the atomic coordinates, so the junction epitope is unresolved.
- Experimental complexes B-EXP-001 (MR1/1I8K) and B-EXP-002 (34E5/8UKV) remain stronger pose evidence than either predicted docking run.

Primary support for the HuCL47 restraint set: [Balyasnikova et al., 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3436275/) reported clone-47 competition with IL-13 and tested IL13Rα2 Tyr207, Asp271, Tyr315 and Asp318 mutations.
