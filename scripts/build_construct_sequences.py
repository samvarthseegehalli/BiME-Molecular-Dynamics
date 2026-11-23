#!/usr/bin/env python3
"""Generate traceable tandem-antibody construct sequences for both tracks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCFV_LINKER = "GGGGSGGGGSGGGGS"       # (G4S)3, 15 aa
ARM_LINKER = "GGGGSGGGGSGGGGSGGGGS"  # (G4S)4, 20 aa

DOMAINS = {
    "B6H12.2_VH": "EVKLVESGGDLVKPGGSLKLSCAASGFTFSGYGMSWVRQTPDKRLEWVATITSGGTYTYYPDSVKGRFTISRDNAKNTLYLQIDSLKSEDTAIYFCARSLAGNAMDYWGQGTSVTVSS",
    "B6H12.2_VL": "DIVMTQSPATLSVTPGDRVSLSCRASQTISDYLHWYQQKSHESPRLLIKFASQSISGIPSRFSGSGSGSDFTLSINSVEPEDVGVYYCQNGHGFPRTFGGGTKLEIK",
    "KWAR23_VH": "EVQLQQSGAELVKPGASVKLSCTASGFNIKDYYIHWVQQRTEQGLEWIGRIDPEDGETKYAPKFQDKATITADTSSNTAYLHLSSLTSEDTAVYYCARWGAYWGQGTLVTVSA",
    "KWAR23_VL": "IVLTQSPAIMSASPGEKVTLTCASSSVSSSYLYWYQQKPGSSPKLWIYSTSNLASGVPARFSGSGSGTSYSLTISSMEAEDAASYFCHQWSSYPRTFGAGTKLELK",
    "34E5_VHH": "EVQLVESGGGLVQPGGSLRLSCTASGMIFSFNVMGWYRQAPGNQRELAATITTDGSTNYADSVKGRFTISRDKNTVYLQMNSLKPEDTAVYYCHLKNIRDYRNYSNYWGQGTQVTVSS",
    "HuCL47_VH": "QVQLVQSGAEVKKPGASVKVSCKASGYTFSNYLMNWVRQAPGQGLEWMGRIDPYDGDIDYNQNFKDRVTITRDTSASTAYMELSSLRSEDTAVYYCARGYGTAYGVDYWGQGTSVTVSS",
    "HuCL47_VL": "EIVLTQSPATLSLSPGERATLSCRASESVDNYGISFMNWYQQKPGQAPRLLIYAASRQGSGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQSKEVPWTFGGGTKLEIK",
}


def scfv(name: str) -> str:
    return DOMAINS[f"{name}_VH"] + SCFV_LINKER + DOMAINS[f"{name}_VL"]


CONSTRUCTS = {
    # Track A orientation pair. The forward design is the primary sequence;
    # the reverse order is a bounded architecture control.
    "A-FC-001_B6H12.2_scfv__KWAR23_scfv": scfv("B6H12.2") + ARM_LINKER + scfv("KWAR23"),
    "A-FC-002_KWAR23_scfv__B6H12.2_scfv": scfv("KWAR23") + ARM_LINKER + scfv("B6H12.2"),
    # Track B checkpoint-target variants using the experimentally solved 34E5
    # VHH-EGFRvIII complex as the tumor-directed arm.
    "B-FC-001_34E5_VHH__KWAR23_scfv": DOMAINS["34E5_VHH"] + ARM_LINKER + scfv("KWAR23"),
    "B-FC-002_34E5_VHH__B6H12.2_scfv": DOMAINS["34E5_VHH"] + ARM_LINKER + scfv("B6H12.2"),
    # A second tumor-antigen route retained for sensitivity analysis. HuCL47
    # has exact public VH/VL sequences but only a predicted binding pose.
    "B-FC-003_HuCL47_scfv__KWAR23_scfv": scfv("HuCL47") + ARM_LINKER + scfv("KWAR23"),
    "B-FC-004_HuCL47_scfv__B6H12.2_scfv": scfv("HuCL47") + ARM_LINKER + scfv("B6H12.2"),
}


def write_fasta(path: Path, records: dict[str, str]) -> None:
    with path.open("w") as handle:
        for name, sequence in records.items():
            if set(sequence) - set("ACDEFGHIKLMNPQRSTVWY"):
                raise ValueError(f"nonstandard amino acid in {name}")
            handle.write(f">{name}|length={len(sequence)}\n")
            for start in range(0, len(sequence), 80):
                handle.write(sequence[start : start + 80] + "\n")


def main() -> None:
    a_dir = ROOT / "track-a-general-cd47-sirpa" / "constructs" / "sequences"
    b_dir = ROOT / "track-b-glioblastoma-targeted" / "constructs" / "sequences"
    a_dir.mkdir(parents=True, exist_ok=True)
    b_dir.mkdir(parents=True, exist_ok=True)
    write_fasta(a_dir / "component_domains.fasta", {k: v for k, v in DOMAINS.items() if k.startswith(("B6H12", "KWAR23"))})
    write_fasta(a_dir / "candidate_constructs.fasta", {k: v for k, v in CONSTRUCTS.items() if k.startswith("A-")})
    write_fasta(b_dir / "component_domains.fasta", DOMAINS)
    write_fasta(b_dir / "candidate_constructs.fasta", {k: v for k, v in CONSTRUCTS.items() if k.startswith("B-")})


if __name__ == "__main__":
    main()
