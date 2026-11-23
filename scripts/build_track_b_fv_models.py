#!/usr/bin/env python3
"""Build Track B antibody Fv models with ABodyBuilder2.

The input sequences are copied from the provenance-tracked FASTA files.  The
models are screening inputs for docking, not experimental structures.
"""

from pathlib import Path

from ImmuneBuilder import ABodyBuilder2


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "track-b-glioblastoma-targeted" / "structures" / "predicted-fv"
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = {
    "2173": {
        "H": "EIQLVQSGAEVKKPGESLRISCKGSGFNIEDYYIHWVRQMPGKGLEWMGRIDPENDETKYGPIFQGHVTISADTSINTVYLQWSSLKASDTAMYYCAFRGGVYWGQGTTVTVSS",
        "L": "DVVMTQSPDSLAVSLGERATINCKSSQSLLDSDGKTYLNWLQQKPGQPPKRLISLVSKLDSGVPDRFSGSGSGTDFTLTISSLQAEDVAVYYCWQGTHFPGTFGGGTKVEIK",
    },
    "HuCL47": {
        "H": "QVQLVQSGAEVKKPGASVKVSCKASGYTFSNYLMNWVRQAPGQGLEWMGRIDPYDGDIDYNQNFKDRVTITRDTSASTAYMELSSLRSEDTAVYYCARGYGTAYGVDYWGQGTSVTVSS",
        "L": "EIVLTQSPATLSLSPGERATLSCRASESVDNYGISFMNWYQQKPGQAPRLLIYAASRQGSGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQSKEVPWTFGGGTKLEIK",
    },
}


def main() -> None:
    predictor = ABodyBuilder2()
    for name, sequences in CANDIDATES.items():
        output = OUT / f"{name}_ABodyBuilder2.pdb"
        antibody = predictor.predict(sequences)
        antibody.save(str(output))
        print(output)


if __name__ == "__main__":
    main()
