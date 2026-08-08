from src.ingestion.models import ParsedDocument, ParsedSection
from src.shared.exceptions import ParsingError


class DoclingParser:
    """Wraps docling's DocumentConverter to produce structure-preserving
    (section/page aware) text, rather than flattening the document to raw text.

    docling is imported lazily so this module (and anything that imports it)
    doesn't require the heavy docling/torch dependency chain unless a
    DoclingParser is actually instantiated.
    """

    def __init__(self):
        from docling.document_converter import DocumentConverter

        self._converter = DocumentConverter()

    def parse(self, file_path: str) -> ParsedDocument:
        try:
            result = self._converter.convert(file_path)
        except Exception as exc:
            raise ParsingError(f"docling failed to parse {file_path}: {exc}") from exc

        doc = result.document
        sections: list[ParsedSection] = []
        current_section: str | None = None

        for item, _level in doc.iterate_items():
            text = getattr(item, "text", None)
            if not text:
                continue

            label = str(getattr(item, "label", ""))
            if "section" in label.lower() or "title" in label.lower():
                current_section = text

            page = None
            prov = getattr(item, "prov", None)
            if prov:
                page = getattr(prov[0], "page_no", None)

            sections.append(ParsedSection(text=text, section=current_section, page=page))

        return ParsedDocument(sections=sections)
