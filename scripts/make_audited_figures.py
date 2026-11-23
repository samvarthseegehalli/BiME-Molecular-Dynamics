#!/usr/bin/env python3
"""Generate the portable, data-backed figure subset from packaged artifacts.

The original full manuscript figure builder depended on a historical paper-data
tree and rendered structure images that are not in this compact repository.
This entry point now generates the reproducible interface-contact figure from
the included XVG observations. Use ``--data-dir`` and ``--output`` to override
the repository defaults.
"""

from make_artifact_figures import main


if __name__ == "__main__":
    raise SystemExit(main())
