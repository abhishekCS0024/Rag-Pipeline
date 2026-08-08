from infrastructure.parsing.docling_parser import DoclingParser
from src.ingestion.models import ParsedDocument


class DocumentParser:
    def __init__(self, docling_parser: DoclingParser | None = None):
        self._docling_parser = docling_parser or DoclingParser()

    def parse(self, file_path: str) -> ParsedDocument:
        return self._docling_parser.parse(file_path)
