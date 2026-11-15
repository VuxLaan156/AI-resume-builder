from .DocumentExtractor import DocumentExtractor, TextBlock


class TxtExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> list[TextBlock]:
        return [TextBlock(text=data.decode("utf-8-sig"))]