import json
from collections.abc import Callable

from infrastructure.rabbitmq.connection import get_connection
from infrastructure.rabbitmq.topology import declare_topology
from src.shared.config import get_settings
from src.shared.logging import get_logger

logger = get_logger(__name__)


def consume_queue(queue_name: str, handler: Callable[[dict], None]) -> None:
    """Blocking consume loop. A handler failure rejects the message without
    requeue, which routes it straight to the DLQ (per the queue's
    dead-letter-exchange arguments declared in topology.py).
    # ponytail: no retry-with-backoff via the retry queue yet; add if
    # transient failures (e.g. a flaky embedding API call) turn out to need it.
    """
    settings = get_settings()
    connection = get_connection()
    channel = connection.channel()
    declare_topology(channel, settings)
    channel.basic_qos(prefetch_count=settings.rabbitmq_prefetch_count)

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
            handler(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("failed to process message from %s", queue_name)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()
