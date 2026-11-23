# BiME molecular-dynamics research repository

## Research paper

**In Silico Assembly and Molecular Dynamics Evaluation of an EGFRvIII–SIRPα Bispecific Binder for Glioblastoma-Associated Targeting**

[**Read or download the full paper (PDF)**](Research_Paper.pdf)

This repository contains the clean final manuscript, recovered computational source, and a compact scientific artifact package for an in-silico EGFRvIII–SIRPα bispecific binder (BiME). The study assembles a 372-residue Fc-free tandem construct from experimentally resolved parent interfaces, prepares four soluble structural states, evaluates docking controls, and analyzes three independently velocity-initialized 20 ns GROMACS trajectories per state.

The results support only short-timescale structural observations for the modeled soluble fragments: local domain persistence, persistent contacts in prepositioned interfaces, and replica-dependent accessibility. They do not demonstrate fusion affinity, selectivity, checkpoint inhibition, cell-surface bridging, safety, or therapeutic efficacy. The manuscript also records limitations including omitted alternative ranked docking poses, no second docking engine, no full-length/glycosylated membrane model, no established multidomain convergence, no aggregation assessment, and no experimental validation.

## Quick start

From the repository root, verify all 786 public scientific artifacts using only the Python standard library:

```sh
python3 scripts/verify_manifest.py
```

The verifier fails if any listed file is missing, has the wrong byte count, or does not match its SHA-256. The included observable tables can be inspected without GROMACS. Raw trajectories are archived separately; see [ARTIFACT_SCOPE.md](ARTIFACT_SCOPE.md).

Recompute the packaged replica and aggregate statistics directly from the archived XVG time series:

```sh
python3 scripts/verify_paper_data.py
python3 -m unittest discover -s tests -v
```

Generate the reproducible interface-contact figure (SVG, standard library only):

```sh
python3 scripts/make_audited_figures.py
python3 scripts/plot_thermo.py
```

The default outputs are `results/figures/interface_contacts.svg` and `results/figures/thermodynamic_summary.svg`. Override inputs and output with `--data-dir` and `--output`.

To inspect the original analysis commands for a replica, install GROMACS 2025.1 and run the script in dry-run mode with that replica's archived input and trajectory directory:

```sh
python3 scripts/analyze_construct_replica.py /path/to/00_unbound/replica-01
```

It prints the GROMACS commands without executing them. Add `--execute` only when the matching `.tpr` and `.xtc` are present and you intend to regenerate observables. The compact artifact package has `.tpr` files and derived `.xvg` outputs but omits `.xtc` trajectories.

## Repository map

- [scripts/](scripts/) — recovered preparation, docking-QC, MD analysis, and manuscript-data scripts; see [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for portability limitations.
- [artifacts/](artifacts/) — 786 manifest-listed structures, inputs, outputs, metadata, and tables.
- [Submission_Final_Staging/BiME_Artifact_Metadata/](Submission_Final_Staging/BiME_Artifact_Metadata/) — package README and source inventory.
- [Submission_Final_Staging/Revised_Standard_Manuscript.pdf](Submission_Final_Staging/Revised_Standard_Manuscript.pdf) — clean manuscript retained from the project folder; the root `Research_Paper.pdf` is the release copy.
- [DATA.md](DATA.md), [ARTIFACT_SCOPE.md](ARTIFACT_SCOPE.md), and [REPRODUCIBILITY.md](REPRODUCIBILITY.md) — provenance, coverage, and execution details.

## Scope and interpretation

This is a computational structural study. Static docking scores and finite 20 ns trajectories cannot establish binding affinity or biological function. Refer to the clean manuscript and reproducibility notes for reported findings and unperformed evaluations.

## Citation, environment, and release notes

See [CITATION.cff](CITATION.cff) and [environment.yml](environment.yml). The environment pins the recovered core packages and explicit preparation/plotting package versions; it has not yet been clean-installed as a complete environment. It does not recreate the historical GPU host. The [MIT license](LICENSE) covers original source code only. The clean manuscript is provided for reading under its own rights; see [DATA.md](DATA.md) for the PDB coordinate provenance and external trajectory archive. This public copy omits reviewer correspondence, reviewer-coverage ledgers, tracked-change drafts, alternate manuscript variants, and generated QA page renders. The PDB archive coordinates are identified in the manifest and covered by the CC0 policy noted in [DATA.md](DATA.md).
