# Reproducibility guide

## Lightweight route

Run `python3 scripts/verify_manifest.py` from the repository root. It uses only Python's standard library and checks every row in `artifacts/PACKAGE_FILE_MANIFEST.csv` against `artifacts/`. A nonzero exit code indicates a missing or altered file. This validates package integrity, not the scientific correctness of the analysis.

Run `python3 scripts/verify_paper_data.py` to recompute all 216 replica-metric rows and 72 aggregate rows from the packaged XVG observations. It uses only the Python standard library and defaults to the repository's `artifacts/` directory; `--data-dir` accepts a relocated package root. Run `python3 -m unittest discover -s tests -v` for the numerical, unit-conversion, and residue-mapping checks.

The published summary tables are in `artifacts/Analysis_Tables/manuscript_tables/`. Per-replica time series are saved in the GROMACS `.xvg` files under `artifacts/MD_Reproducibility/systems/`. Aggregate means and sample SDs summarize the three replica time averages; time points are not treated as independent replicas. Definitions, windows, and limitations are described in the authoritative clean manuscript.

## Recompute observables

The recovered `scripts/analyze_construct_replica.py` prints the GROMACS commands by default. Given a replica folder containing matching `md_20ns.tpr` and `md_20ns.xtc`, run:

```sh
python3 scripts/analyze_construct_replica.py /path/to/replica-01
```

Then add `--execute` to run them. This generates RMSD/RMSF, radius of gyration, SASA, interface contacts, minimum distances, and hydrogen-bond counts. Its selections and command details are in the script. The artifact package lacks XTC trajectories, so use the separately retained archive listed in `artifacts/MD_Reproducibility/trajectory_archive_manifest.csv`. Confirm file sizes and match the corresponding TPR before analysis.

## Full simulation

GROMACS 2025.1 was used. The included production `.mdp` files specify 2 fs timestep, 10,000,000 steps (20 ns), LINCS constraints on bonds to hydrogen, PME electrostatics, 1.0 nm Coulomb and van der Waals cutoffs, V-rescale thermostat at 310 K, and isotropic C-rescale pressure coupling at 1 bar. The project handoff records AMBER99SB-ILDN, TIP3P, neutralization plus nominal 0.15 M NaCl, dodecahedral boxes with 1.2 nm initial solute padding. The exact input files remain authoritative for each stage. Original production used GPU-enabled cluster builds; the available local GROMACS 2025.1 build is CPU-only. Numerical trajectories can vary with hardware, parallel reductions, and binary build.

The compact package is not a clean-checkout full simulation environment: raw trajectories are excluded, some stage records contain original cluster absolute paths, force-field distribution is separate, and no tested dependency lock/container was recovered. Preparation scripts requiring Python packages have no verified pinned environment. Reproduction at full simulation scale needs the external trajectory archive and original compute setup. No simulation rerun is performed by the lightweight validation command.

## Figure and table traceability

- Tables and numerical summaries: `artifacts/Analysis_Tables/` and `artifacts/Analysis_Tables/manuscript_tables/`.
- Trajectory observables behind MD plots: per-replica GROMACS `.xvg` files in `artifacts/MD_Reproducibility/systems/<state>/<replica>/analysis_from_0ns/` and `binding_accessibility_500ps/`.
- Docking setup and retained poses: `artifacts/Docking_Reproducibility/`; candidate scores: `artifacts/Analysis_Tables/candidate_screen_scores.csv`.
- Starting models, mappings, and integrity records: `artifacts/Coordinates/` and `artifacts/Reference_Structures/`.
- Reproducible packaged figures: `python3 scripts/make_audited_figures.py --output results/figures/interface_contacts.svg` plots single/dual interface contacts from XVG time series; `python3 scripts/plot_thermo.py --output results/figures/thermodynamic_summary.svg` plots archived per-replica thermodynamic summary values. Both accept `--data-dir` and use the standard library. Other manuscript figures require historical structure renders or trajectory data not included in this package.
