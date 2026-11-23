# Artifact scope

| Activity | Available here | What it supports |
|---|---|---|
| Verify packaged data | Yes | Checks all 786 public inventory entries for path, size, and SHA-256 |
| Inspect models and mappings | Yes | Review of packaged coordinates and provenance maps |
| Recompute summary statistics from saved observables | Yes | Replica summaries from included `.xvg` files or machine-readable tables |
| Recompute trajectory observables | Not from compact package alone | Raw XTC frames are excluded; matching trajectories remain in the separate USB archive described by `artifacts/MD_Reproducibility/trajectory_archive_manifest.csv` |
| Rerun MD | Inputs are substantially represented; trajectories are external | Requires GROMACS 2025.1, substantial CPU/GPU resources, external force-field files, and the archived system/trajectory layout |
| Reproduce every docking search | No | HDOCK web jobs and retained outputs are documented; alternative ranked poses are omitted, and no second docking engine was run |
| Validate biological function | No | No experimental binding, competition, cell, phagocytosis, safety, or efficacy data are included |

The 12 production trajectories are four states × three velocity-initialized replicas × 20 ns (240 ns total). Seeds are in `artifacts/Analysis_Tables/manuscript_tables/completion_and_seeds.csv`. A shared prepared starting geometry was used per state; independent initial velocities do not establish independent conformational starting ensembles. Saved observables permit checking published summaries but do not establish convergence.
