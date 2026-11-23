# Data provenance and rights

## Structural sources

The packaged `artifacts/Reference_Structures/reference_structure_manifest.csv` identifies the PDB-derived structures, their roles, source archive paths, sizes, and SHA-256 values. The principal experimental templates are PDB 8UKV (34E5–EGFRvIII), 6BIT (KWAR23–SIRPα), and 2JJS (native CD47–SIRPα comparison). Additional candidate and redocking-control records are listed in that manifest. Coordinate/chain mappings and construct residue mappings are in `artifacts/Coordinates/`.

These structures were recovered from the project archive on 23 November 2026. Their original database download/access dates were not recorded in the supplied manifest. The RCSB PDB states that files in the PDB archive are available under CC0 1.0; it encourages attribution to the original structure authors. See the [RCSB PDB usage policy](https://www2.rcsb.org/pages/usage-policy).

## Derived and modeled data

Four soluble-state starting structures, docking inputs/outputs, GROMACS input/settings and derived observable tables are in `artifacts/`. Coordinate provenance, construct maps, and source residue mappings accompany the structures. Models are computationally assembled from resolved parent interfaces; they are not experimentally determined BiME structures. The raw XTC trajectories are outside this repository; see the explicit archive paths and byte counts in `artifacts/MD_Reproducibility/trajectory_archive_manifest.csv`.

## Software and permissions

The repository's MIT `LICENSE` applies only to original project source code and associated code documentation. The PDB archive coordinates in the reference-structure manifest are CC0 1.0; this does not change the rights in manuscript or reviewer materials. The public release includes the author-supplied clean final manuscript and excludes reviewer correspondence, tracked changes, alternate manuscript versions, and temporary QA renders. Raw trajectories remain in the separate archive listed above.
