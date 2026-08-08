import sys
import types

import pytest

from src.shared.exceptions import ParsingError


class FakeProv:
    def __init__(self, page_no):
        self.page_no = page_no


class FakeItem:
    def __init__(self, text=None, label="", prov=None):
        self.text = text
        self.label = label
        self.prov = prov


class FakeDoclingDocument:
    def __init__(self, items):
        self._items = items

    def iterate_items(self):
        yield from self._items


class FakeConvertResult:
    def __init__(self, document):
        self.document = document


class FakeDocumentConverter:
    """Stand-in for docling.document_converter.DocumentConverter."""

    result: FakeConvertResult | None = None
    raise_on_convert: Exception | None = None
    received_paths: list[str] = []

    def convert(self, file_path):
        FakeDocumentConverter.received_paths.append(file_path)
        if FakeDocumentConverter.raise_on_convert:
            raise FakeDocumentConverter.raise_on_convert
        return FakeDocumentConverter.result


@pytest.fixture
def fake_docling(monkeypatch):
    """Injects a fake docling.document_converter module so DoclingParser's
    lazy `from docling.document_converter import DocumentConverter` succeeds
    without the real (heavy) docling package installed.
    """
    FakeDocumentConverter.result = None
    FakeDocumentConverter.raise_on_convert = None
    FakeDocumentConverter.received_paths = []

    fake_docling_pkg = types.ModuleType("docling")
    fake_submodule = types.ModuleType("docling.document_converter")
    fake_submodule.DocumentConverter = FakeDocumentConverter

    monkeypatch.setitem(sys.modules, "docling", fake_docling_pkg)
    monkeypatch.setitem(sys.modules, "docling.document_converter", fake_submodule)

    # docling_parser must be (re)imported fresh under the faked sys.modules.
    sys.modules.pop("infrastructure.parsing.docling_parser", None)
    import infrastructure.parsing.docling_parser as docling_parser_module

    yield docling_parser_module
    sys.modules.pop("infrastructure.parsing.docling_parser", None)


def test_parse_builds_sections_tracking_current_heading_and_page(fake_docling):
    items = [
        (FakeItem(text="Intro", label="section_header", prov=[FakeProv(page_no=1)]), 0),
        (FakeItem(text="First paragraph.", label="paragraph", prov=[FakeProv(page_no=1)]), 1),
        (FakeItem(text="Body", label="title", prov=[FakeProv(page_no=2)]), 0),
        (FakeItem(text="Second paragraph.", label="paragraph", prov=[FakeProv(page_no=2)]), 1),
    ]
    FakeDocumentConverter.result = FakeConvertResult(FakeDoclingDocument(items))

    parser = fake_docling.DoclingParser()
    parsed = parser.parse("/tmp/sample.pdf")

    assert [s.text for s in parsed.sections] == ["Intro", "First paragraph.", "Body", "Second paragraph."]
    assert [s.section for s in parsed.sections] == ["Intro", "Intro", "Body", "Body"]
    assert [s.page for s in parsed.sections] == [1, 1, 2, 2]
    assert FakeDocumentConverter.received_paths == ["/tmp/sample.pdf"]


def test_parse_skips_items_with_no_text(fake_docling):
    items = [
        (FakeItem(text=None, label="picture", prov=None), 0),
        (FakeItem(text="", label="paragraph", prov=None), 0),
        (FakeItem(text="kept", label="paragraph", prov=None), 0),
    ]
    FakeDocumentConverter.result = FakeConvertResult(FakeDoclingDocument(items))

    parsed = fake_docling.DoclingParser().parse("/tmp/sample.pdf")

    assert [s.text for s in parsed.sections] == ["kept"]


def test_parse_sets_page_none_when_item_has_no_provenance(fake_docling):
    items = [(FakeItem(text="no page info", label="paragraph", prov=None), 0)]
    FakeDocumentConverter.result = FakeConvertResult(FakeDoclingDocument(items))

    parsed = fake_docling.DoclingParser().parse("/tmp/sample.pdf")

    assert parsed.sections[0].page is None


def test_parse_wraps_converter_failure_in_parsing_error(fake_docling):
    FakeDocumentConverter.raise_on_convert = RuntimeError("corrupt file")

    parser = fake_docling.DoclingParser()

    with pytest.raises(ParsingError):
        parser.parse("/tmp/broken.pdf")
