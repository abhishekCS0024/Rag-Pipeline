from apps.worker.handlers.process_document import handle_document_uploaded
from infrastructure.rabbitmq.consumer import consume_queue
from src.shared.config import get_settings


def run() -> None:
    settings = get_settings()
    consume_queue(settings.rabbitmq_process_queue, handle_document_uploaded)
