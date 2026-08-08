import json
import uuid

import pytest

from infrastructure.rabbitmq.publisher import publish_document_uploaded
from src.shared.config import Settings


class FakeChannel:
    def __init__(self, raise_on_publish: Exception | None = None):
        self.published: list[dict] = []
        self._raise = raise_on_publish

    def basic_publish(self, exchange, routing_key, body, properties):
        if self._raise:
            raise self._raise
        self.published.append(
            {"exchange": exchange, "routing_key": routing_key, "body": body, "properties": properties}
        )


class FakeConnection:
    def __init__(self, channel: FakeChannel):
        self._channel = channel
        self.closed = False

    def channel(self):
        return self._channel

    def close(self):
        self.closed = True


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_publish_sends_event_json_to_configured_exchange_and_routing_key(monkeypatch):
    channel = FakeChannel()
    connection = FakeConnection(channel)
    settings = _settings()
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.get_settings", lambda: settings)
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.get_connection", lambda: connection)
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.declare_topology", lambda channel, settings: None)
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    publish_document_uploaded(document_id, tenant_id, "tenants/x/documents/y/doc.pdf")

    assert len(channel.published) == 1
    message = channel.published[0]
    assert message["exchange"] == settings.rabbitmq_document_exchange
    assert message["routing_key"] == settings.rabbitmq_process_routing_key
    body = json.loads(message["body"])
    assert body == {
        "event": "document.uploaded",
        "document_id": str(document_id),
        "tenant_id": str(tenant_id),
        "s3_key": "tenants/x/documents/y/doc.pdf",
    }
    assert connection.closed is True


def test_publish_closes_connection_even_when_publish_raises(monkeypatch):
    channel = FakeChannel(raise_on_publish=RuntimeError("broker down"))
    connection = FakeConnection(channel)
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.get_settings", lambda: _settings())
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.get_connection", lambda: connection)
    monkeypatch.setattr("infrastructure.rabbitmq.publisher.declare_topology", lambda channel, settings: None)

    with pytest.raises(RuntimeError):
        publish_document_uploaded(uuid.uuid4(), uuid.uuid4(), "key")

    assert connection.closed is True
