"""Full-stack check: requires `make up` + `make migrate`, a real embedding
API key configured, and RabbitMQ reachable. Run explicitly with `pytest -m e2e`.

Runs the worker handler in-process after upload rather than requiring a
separately-running `make run-worker` process, so the test stays self-contained.
"""
import io
import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.worker.handlers.process_document import handle_document_uploaded
from infrastructure.postgres.repositories.document_repository import SqlDocumentRepository
from infrastructure.postgres.session import SessionLocal
from src.shared.constants import DocumentStatus

pytestmark = pytest.mark.e2e


def test_upload_then_process_reaches_completed():
    client = TestClient(app)

    response = client.post(
        "/documents",
        files={"file": ("sample.txt", io.BytesIO(b"OAuth 2.0 is used for authentication."), "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    document_id = uuid.UUID(body["document_id"])
    assert body["status"] == DocumentStatus.UPLOADED

    session = SessionLocal()
    tenant_id = SqlDocumentRepository(session).get_by_id(document_id).tenant_id
    session.close()

    handle_document_uploaded({"document_id": str(document_id), "tenant_id": str(tenant_id)})

    status_response = client.get(f"/documents/{document_id}")
    assert status_response.json()["status"] == DocumentStatus.COMPLETED
