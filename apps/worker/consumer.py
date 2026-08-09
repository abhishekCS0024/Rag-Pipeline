# Blocking consume loop that wires RabbitMQ queues to their handler callbacks.
from apps.worker.handlers.delete_document import handle_document_delete
from apps.worker.handlers.process_document import handle_document_uploaded
from apps.worker.handlers.reindex_document import handle_document_reindex
from infrastructure.rabbitmq.consumer import consume_queues
from src.shared.config import get_settings


def run() -> None:
    settings = get_settings()
    consume_queues(
        {
            settings.rabbitmq_process_queue: handle_document_uploaded,
            settings.rabbitmq_reindex_queue: handle_document_reindex,
            settings.rabbitmq_delete_queue: handle_document_delete,
        }
    )
