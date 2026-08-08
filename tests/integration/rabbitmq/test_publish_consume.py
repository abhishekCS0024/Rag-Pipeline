"""Requires `make up` (real RabbitMQ reachable via .env)."""
import json
import uuid

from infrastructure.rabbitmq.connection import get_connection
from infrastructure.rabbitmq.publisher import publish_document_uploaded
from infrastructure.rabbitmq.topology import declare_topology
from src.shared.config import get_settings


def test_publish_then_basic_get_roundtrip():
    document_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    publish_document_uploaded(document_id, tenant_id, "tenants/x/documents/y/doc.pdf")

    settings = get_settings()
    connection = get_connection()
    try:
        channel = connection.channel()
        declare_topology(channel, settings)

        method, _properties, body = channel.basic_get(settings.rabbitmq_process_queue, auto_ack=True)
        assert method is not None

        payload = json.loads(body)
        assert payload["document_id"] == str(document_id)
        assert payload["tenant_id"] == str(tenant_id)
    finally:
        connection.close()
