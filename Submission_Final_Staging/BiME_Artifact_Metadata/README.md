# Compact BiME Reviewer-Support Data Package

Prepared 29 September 2026. This package documents computational methods, structural models, and quantitative results for the clean manuscript. The public copy omits reviewer correspondence, tracked changes, alternate manuscript versions, and generated QA renders.

## Included

- The 372-residue construct sequence and four prepared soluble-state starting-coordinate PDBs: unbound, EGFRvIII-fragment-bound, SIRPα-IgV-bound, and dual-bound. Sequence, chain/domain, target-to-source residue mapping, and coordinate-integrity records are included.
- Reference structures used for the reported binder-screening and native-interface comparisons.
- HDOCK input structures, job manifest, scoring outputs, selected/accepted complexes, concise selection and quality-control records, and one top-ranked pose per archived job. The other ranked-pose coordinate files are omitted; the package is not a complete archive of every ranked model.
- Machine-readable manuscript result tables, candidate-screening scores, native-interface comparison scores, and available PRODIGY inputs and logs.
- Molecular-dynamics parameter files and completion logs; the twelve exact production .tpr inputs; topology files; production logs and energy files; analysis selections; per-frame .xvg observables; and replica-level and aggregate analysis tables. Intermediate solvated snapshots and checkpoint files are omitted.

## Trajectories and scope

The reported production consists of 12 trajectories (four modeled states × three independently velocity-initialized replicas), each 20 ns. The XTC trajectory files listed in `MD_Reproducibility/trajectory_archive_manifest.csv` are not included in this package. The manifest records their archived paths and byte sizes; the listed files total 28,385,906,408 bytes (28.39 GB decimal; 26.44 GiB), including the production trajectories and associated equilibration, pilot, or processed trajectory files recorded there. The manuscript's reported replica-level metrics and available analysis outputs are included, but the raw trajectory frames are not available in this package for independent recalculation.

This package supports inspection of prepared structural models, simulation inputs, computational settings, and reported analyses. It does not establish simulation convergence, fusion affinity, biological specificity, checkpoint inhibition, membrane-spanning geometry, or experimental activity. The clean manuscript and [ARTIFACT_SCOPE.md](../../ARTIFACT_SCOPE.md) document analyses and validations that remain partial or unperformed, including aggregation assessment, membrane/glycan context, and experimental binding and functional assays. No separate Supplementary Information document is included.


## Public release note

The public repository retains the clean manuscript and scientific artifact files. Reviewer correspondence, reviewer coverage ledgers, tracked-change variants, alternate manuscript files, and QA page renders are omitted. The package inventories therefore list 786 public scientific artifacts.
