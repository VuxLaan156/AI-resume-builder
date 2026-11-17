"""Run a live JD extraction smoke test with NVIDIA Nemotron Bolt."""

import argparse
from pathlib import Path

import requests

from backend.app.schemas.job_descriptions import JDAnalysis
from backend.app.services.jd_analyzer import analyze_jd
from backend.app.services.rag.document_loader import load_document

DEFAULT_JD = Path(__file__).with_name("JD 1 - AI & Machine Learning Engineer.pdf")


def extract_jd(path: Path) -> JDAnalysis:
    return analyze_jd(load_document(path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=DEFAULT_JD)
    args = parser.parse_args()
    try:
        result = extract_jd(args.source)
        if result.title is None or not result.required_skills:
            raise ValueError("Expected a job title and at least one required skill")
    except (OSError, RuntimeError, ValueError, requests.RequestException) as exc:
        parser.exit(1, f"JD extraction failed: {exc}\n")
    print(result.model_dump_json(indent=2, exclude_none=True))


if __name__ == "__main__":
    main()
