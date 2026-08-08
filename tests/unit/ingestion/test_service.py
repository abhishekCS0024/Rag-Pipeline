import uuid

from src.documents.models import Document
from src.ingestion.models import ParsedDocument, ParsedSection
from src.ingestion.service import IngestionService
from src.shared.config import Settings
from src.shared.constants import DocumentStatus


class FakeStorage:
    def __init__(self, content: bytes):
        self._content = content
        self.downloaded_keys: list[str] = []

    def upload(self, key, fileobj, content_type):
        raise NotImplementedError

    def download(self, key):
        self.downloaded_keys.append(key)
        return self._content

    def delete(self, key):
        raise NotImplementedError


class FakeParser:
    def __init__(self, parsed: ParsedDocument):
        self._parsed = parsed
        self.paths: list[str] = []

    def parse(self, file_path):
        self.paths.append(file_path)
        return self._parsed


def _document(**overrides) -> Document:
    defaults = dict(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        filename="report.pdf",
        content_type="application/pdf",
        storage_key="tenants/x/documents/y/report.pdf",
        status=DocumentStatus.PROCESSING,
        checksum=None,
        created_at=None,
        updated_at=None,
    )
    defaults.update(overrides)
    return Document(**defaults)


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
        chunk_size=50,
        chunk_overlap=0,
        include_section_metadata=True,
        include_page_metadata=True,
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_process_downloads_parses_and_chunks_using_configured_settings(monkeypatch):
    monkeypatch.setattr("src.ingestion.service.get_settings", lambda: _settings())
    parsed = ParsedDocument(sections=[ParsedSection(text="hello world", section="Body", page=1)])
    storage = FakeStorage(b"file bytes")
    parser = FakeParser(parsed)
    service = IngestionService(storage, parser)
    document = _document()

    chunks = service.process(document)

    assert storage.downloaded_keys == [document.storage_key]
    assert parser.paths[0].endswith(".pdf")
    assert [c.content for c in chunks] == ["hello world"]
    assert chunks[0].section == "Body"
    assert chunks[0].page == 1


def test_process_strips_metadata_when_settings_disable_it(monkeypatch):
    monkeypatch.setattr(
        "src.ingestion.service.get_settings",
        lambda: _settings(include_section_metadata=False, include_page_metadata=False),
    )
    parsed = ParsedDocument(sections=[ParsedSection(text="hello", section="Body", page=1)])
    service = IngestionService(FakeStorage(b"bytes"), FakeParser(parsed))

    chunks = service.process(_document())

    assert chunks[0].section is None
    assert chunks[0].page is None


def test_process_returns_no_chunks_for_document_with_no_sections(monkeypatch):
    monkeypatch.setattr("src.ingestion.service.get_settings", lambda: _settings())
    service = IngestionService(FakeStorage(b"bytes"), FakeParser(ParsedDocument(sections=[])))

    chunks = service.process(_document())

    assert chunks == []


def test_process_uses_temp_file_suffix_matching_original_filename(monkeypatch):
    monkeypatch.setattr("src.ingestion.service.get_settings", lambda: _settings())
    parser = FakeParser(ParsedDocument(sections=[]))
    service = IngestionService(FakeStorage(b"bytes"), parser)

    service.process(_document(filename="notes.docx"))

    assert parser.paths[0].endswith(".docx")
