from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TextBlock:
    text: str
    page_number: int | None = None


class DocumentExtractor(Protocol):
    def extract(self, data: bytes) -> list[TextBlock]: ...
