# HDOCK redocking controls

These jobs test whether template-free HDOCK can recover experimentally observed antibody–antigen interfaces. The larger Fab/scFv is entered as receptor where practical and the antigen as ligand only when doing so follows the server's size recommendation; chain roles and evaluation are always recorded explicitly. For consistency in this batch, the antigen is entered as receptor and the antibody as ligand.

| Run ID | Antibody | Target | Experimental PDB | HDOCK receptor | HDOCK ligand | Mode | Status | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-RD-001 | Hu5F9-G4/5F9 diabody | CD47 | 5IWL | `5IWL:C` | `5IWL:B` | Template-free | Complete: failed recovery | [6ab2836614ce1](http://hdock.phys.hust.edu.cn/data/6ab2836614ce1/) |
| A-RD-002 | B6H12.2 Fab | CD47 | 5TZU | `5TZU:C` | `5TZU:HL` | Template-free | Complete: rank-1 recovery | [6ab28425544fa](http://hdock.phys.hust.edu.cn/data/6ab28425544fa/) |
| A-RD-003 | C47B161 Fab | CD47 | 5TZT | `5TZT:C` | `5TZT:HL` | Template-free | Complete: sampled at rank 88 | [6ab28455d5eab](http://hdock.phys.hust.edu.cn/data/6ab28455d5eab/) |
| A-RD-004 | C47B222 Fab | CD47 | 5TZ2 | `5TZ2:C` | `5TZ2:HL` | Template-free | Complete: rank-1 recovery | [6ab28476c5ef0](http://hdock.phys.hust.edu.cn/data/6ab28476c5ef0/) |
| A-RD-005 | KWAR23 Fab | SIRPα | 6BIT | `6BIT:H` | `6BIT:IK` | Template-free | Complete: rank-1 recovery | [6ab2849cbc05c](http://hdock.phys.hust.edu.cn/data/6ab2849cbc05c/) |
| A-RD-006 | Clone 119 Fab | SIRPα V1 | 6NMR | `6NMR:S` | `6NMR:HL` | Template-free | Complete: rank-1 recovery | [6ab2863a91363](http://hdock.phys.hust.edu.cn/data/6ab2863a91363/) |
| A-RD-007 | Clone 136 Fab | SIRPα V1 | 6NMS | `6NMS:S` | `6NMS:HL` | Template-free | Complete: rank-1 recovery | [6ab2865e8a001](http://hdock.phys.hust.edu.cn/data/6ab2865e8a001/) |
| A-RD-008 | Clone 115 Fab | SIRPα V1 | 6NMU | `6NMU:S` | `6NMU:HL` | Template-free | Complete: rank-1 recovery | [6ab2867482952](http://hdock.phys.hust.edu.cn/data/6ab2867482952/) |
| A-RD-009 | Clone 3 nonblocking Fab | SIRPα V1 | 6NMT | `6NMT:C` | `6NMT:AB` | Template-free | Complete: native-like rank 6 | [6ab2868fa0e82](http://hdock.phys.hust.edu.cn/data/6ab2868fa0e82/) |
| A-RD-010 | Hu5F9-G4/5F9 diabody | CD47 | 5IWL | `5IWL:C` | `5IWL:B` | Template-free plus experimental binding-site residues | Complete: rank-4 interface recovery | [6ab2c07455d36](http://hdock.phys.hust.edu.cn/data/6ab2c07455d36/) |

## Source-file checksums

| PDB | SHA-256 |
| --- | --- |
| 5IWL | `ef8dde488cf41bfbeed9866f7588a4128e5d085d8a32237ac854528eccde880d` |
| 5TZU | `3afbbc98603a658d829b85eef26275ddbc39b8e2b27f7030b51ec3a2ddae9cc3` |
| 5TZT | `ff88102419d85eb0703d4bffed1e3e172902bbe191a924b428c97de48ef0fb80` |
| 5TZ2 | `b1d813c57022591c1b8e77c3359ca77d7067a116e3e3b71df3d4fa791d835a30` |
| 6BIT | `a2a7f5b1b1553634d206ea5df34f110d0cfe48538613aa8de717b35686b09baf` |
| 6NMR | `f98368a29b151ce6de8e15bb733a63f8722b738cf6025dbf0e13a8328ba82698` |
| 6NMS | `fcefd9063c0dbe810b997b2f772e4daadf42ff0d811c5adcd232a0af2cd48cd7` |
| 6NMU | `8e8ea37305785eb514a94702681ca8eb816b7d40f3a53f0848b21259fb244072` |
| 6NMT | `7f6e4eb3c9e30a7de9df968c11071810660ed2e03742799d5f3c612b1bab3d93` |

## Acceptance gate

For each job, compare the retained HDOCK models with the experimental complex after receptor alignment. Record interface RMSD, ligand RMSD, fraction of native contacts and epitope overlap. The unresolved-antibody batch must not be interpreted until these controls establish whether the protocol recovers the known interfaces.

See [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) for measured recovery and the resulting protocol decision.
