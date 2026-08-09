# Declares exchanges/queues/DLX routing for the process, reindex, and delete pipelines.
import pika

from src.shared.config import Settings


def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel, settings: Settings) -> None:
    channel.exchange_declare(
        exchange=settings.rabbitmq_document_exchange,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(queue=settings.rabbitmq_dlq, durable=True)
    channel.queue_declare(queue=settings.rabbitmq_retry_queue, durable=True)

    for queue, routing_key in (
        (settings.rabbitmq_process_queue, settings.rabbitmq_process_routing_key),
        (settings.rabbitmq_reindex_queue, settings.rabbitmq_reindex_routing_key),
        (settings.rabbitmq_delete_queue, settings.rabbitmq_delete_routing_key),
    ):
        channel.queue_declare(
            queue=queue,
            durable=True,
            arguments={"x-dead-letter-exchange": "", "x-dead-letter-routing-key": settings.rabbitmq_dlq},
        )
        channel.queue_bind(
            queue=queue,
            exchange=settings.rabbitmq_document_exchange,
            routing_key=routing_key,
        )
