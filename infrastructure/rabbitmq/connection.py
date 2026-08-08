import pika

from src.shared.config import get_settings


def get_connection() -> pika.BlockingConnection:
    settings = get_settings()
    return pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
