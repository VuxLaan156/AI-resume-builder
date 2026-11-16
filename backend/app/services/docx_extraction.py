from collections.abc import Iterable, Iterator
from io import BytesIO

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .DocumentExtractor import DocumentExtractor, TextBlock


def _iter_text(blocks: Iterable[Paragraph | Table]) -> Iterator[str]:
    for block in blocks:
        if isinstance(block, Paragraph):
            if text := block.text.strip():
                yield text
        else:
            seen_cells = set()
            for row in block.rows:
                for cell in row.cells:
                    if cell._tc not in seen_cells:
                        seen_cells.add(cell._tc)
                        yield from _iter_text(cell.iter_inner_content())


class DocxExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> list[TextBlock]:
        document = Document(BytesIO(data))
        return [TextBlock(text) for text in _iter_text(document.iter_inner_content())]
