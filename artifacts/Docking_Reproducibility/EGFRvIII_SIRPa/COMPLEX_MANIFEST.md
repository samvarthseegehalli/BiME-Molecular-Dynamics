# Track B complex gate

The PDB files in this directory are immutable working copies of either selected HDOCK poses or experimentally determined complexes. Original docking bundles remain under `../docking/<run-id>/hdock-results/`; experimental sources remain under `../structures/`.

## Accepted for structural and PRODIGY screening

| Run | Complex | Selected model | Recovery evidence | File | SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| B-RD-001 | mAb806–EGFR epitope peptide | 1 | LRMSD 0.463 Å; Fnat 1.0000 | `accepted/B-RD-001_mAb806_EGFRpeptide_rank001.pdb` | `aa6599c7e7b0bd59662ea51d6b657aaf9652d9ca78c2510236ffebeebc028241` |
| B-RD-002 | Cetuximab–EGFR | 1 | LRMSD 0.676 Å; Fnat 1.0000 | `accepted/B-RD-002_cetuximab_EGFR_rank001.pdb` | `0ee60181864664f94379957f19b16814ff442307df76341af9150aa595640b39` |
| B-RD-003 | Trastuzumab–HER2 | 2 | LRMSD 0.874 Å; Fnat 0.9787. Rank 1 was incorrect, so model 2 was retained. | `accepted/B-RD-003_trastuzumab_HER2_rank002.pdb` | `bcb014a94b1865111aecc6d4fcb707e29c47da6f51d05cc7ae6545ccbf6ec387` |
| B-EXP-001 | MR1 dsFv–EGFRvIII junction peptide | Experimental PDB 1I8K | Direct crystallographic antibody–neoepitope complex; chains A,B versus C | `accepted/B-EXP-001_MR1_EGFRvIII_peptide_1I8K.pdb` | `45eead39d317e8faff1bf1e0fe5a7e2e3c89d53f8ec3628af46e3b64966d79a5` |
| B-EXP-002 | VHH 34E5–EGFRvIII ectodomain | Experimental PDB 8UKV | Direct crystallographic complex; biological pair chains A and C | `accepted/B-EXP-002_34E5_EGFRvIII_8UKV_AC.pdb` | `b190337cde0462253827650a06c1ecab3264d427c2bfe7b41d8f2a61b9d6a730` |
| B-DOCK-002 | 2173 Fv–EGFRvIII junction peptide | 3 | HDOCK score -141.28; 90% peptide-residue coverage; 16/18 contacted antibody residues in broad CDR ranges; no sub-2.0 Å clash | `accepted/B-DOCK-002_2173_EGFRvIIIjunction_rank003.pdb` | `0df7dcd93c3c9ce5b3f1dae654af2c7159455751727ee1eee94e72f66c8c7722` |
| B-DOCK-001 | HuCL47 Fv–IL13Rα2, global | 34 | Score -207.79; all four experimentally tested receptor residues contacted; 56% CDR-contact fraction; no clash; independently reproduced by B-DOCK-003 | `accepted/B-DOCK-001_HuCL47_IL13RA2_rank034_global.pdb` | `483feb8747dbbc563f5850a10200519d2829ec4fb79b1c27c659487e36ca5442` |
| B-DOCK-003 | HuCL47 Fv–IL13Rα2, guided consensus | 44 | 2.107 Å from global rank 34 after receptor alignment; Fnat 0.9583 to that independent pose; all four tested residues contacted; no clash | `accepted/B-DOCK-003_HuCL47_IL13RA2_rank044_guided_consensus.pdb` | `c368de9f3d6cbb8d6108579a07ae60b06ec24b7a700a1dda4ae7121d53bade13` |

The three redocking complexes validate the workflow and provide comparators. MR1 and 34E5 are experimentally solved EGFRvIII-directed complexes and therefore carry stronger pose evidence than a docking prediction. EGFRvIII is tumor associated, but patient coverage and intratumoral heterogeneity still require explicit discussion; neither structure proves universal glioblastoma specificity.
