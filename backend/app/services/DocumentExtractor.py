from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TextBlock:
    text: str
    page_number: int | None = None


class DocumentExtractor(Protocol):
    def extract(self, data: bytes) -> list[TextBlock]: ...


def write_extracted_text(text_blocks: list[TextBlock], output_path: str | Path) -> None:
    sections = [
        f"[Page {block.page_number}]\n{block.text}"
        if block.page_number is not None
        else block.text
        for block in text_blocks
    ]
    Path(output_path).write_text("\n\n".join(sections), encoding="utf-8")
