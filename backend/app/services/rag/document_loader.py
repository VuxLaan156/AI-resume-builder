from pathlib import Path

from ..DocumentExtractor import TextBlock
from ..extractors import EXTRACTORS


def load_document(path: Path) -> list[TextBlock]:
    extractor = EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return extractor().extract(path.read_bytes())