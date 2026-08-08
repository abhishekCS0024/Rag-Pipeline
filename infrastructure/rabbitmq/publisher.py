import uuid

import pika

from infrastructure.rabbitmq.connection import get_connection
from infrastructure.rabbitmq.messages import DocumentUploadedEvent
from infrastructure.rabbitmq.topology import declare_topology
from src.shared.config import get_settings


def publish_document_uploaded(document_id: uuid.UUID, tenant_id: uuid.UUID, s3_key: str) -> None:
    settings = get_settings()
    event = DocumentUploadedEvent(document_id=document_id, tenant_id=tenant_id, s3_key=s3_key)

    connection = get_connection()
    try:
        channel = connection.channel()
        declare_topology(channel, settings)
        channel.basic_publish(
            exchange=settings.rabbitmq_document_exchange,
            routing_key=settings.rabbitmq_process_routing_key,
            body=event.model_dump_json(),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
    finally:
        connection.close()
