# Entrypoint that starts the background worker process consuming from RabbitMQ.
from apps.worker.consumer import run

if __name__ == "__main__":
    run()
