from src.ingestion.models import ParsedDocument
from src.ingestion.parser import DocumentParser


class FakeDoclingParser:
    def __init__(self):
        self.calls: list[str] = []

    def parse(self, file_path: str) -> ParsedDocument:
        self.calls.append(file_path)
        return ParsedDocument(sections=[])


def test_document_parser_delegates_to_injected_docling_parser():
    fake = FakeDoclingParser()
    parser = DocumentParser(docling_parser=fake)

    result = parser.parse("/tmp/sample.pdf")

    assert fake.calls == ["/tmp/sample.pdf"]
    assert result == ParsedDocument(sections=[])
