import argparse
from pathlib import Path

from .DocumentExtractor import write_extracted_text
from .extractors import EXTRACTORS


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a document to a UTF-8 text file.")
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        default=Path.home() / "Downloads" / "DangVuLan_OnlineCodingContestManagement.pdf",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    extractor = EXTRACTORS.get(args.source.suffix.lower())
    if extractor is None:
        parser.error(f"Unsupported extension. Choose from {', '.join(EXTRACTORS)}.")

    output = args.output or (Path(__file__).resolve().parents[2] / "uploads" / "extracted.txt")
    if output.resolve() == args.source.resolve():
        parser.error("Choose an output file different from the source.")

    blocks = extractor().extract(args.source.read_bytes())
    if not any(block.text.strip() for block in blocks):
        parser.exit(1, "No text extracted.\n")

    output.parent.mkdir(parents=True, exist_ok=True)
    write_extracted_text(blocks, output)
    print(f"Saved {len(blocks)} text blocks to {output}")


if __name__ == "__main__":
    main()
