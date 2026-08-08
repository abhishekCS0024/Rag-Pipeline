from infrastructure.rabbitmq.topology import declare_topology
from src.shared.config import Settings


class FakeChannel:
    def __init__(self):
        self.exchanges: list[dict] = []
        self.queues: list[dict] = []
        self.bindings: list[dict] = []

    def exchange_declare(self, exchange, exchange_type, durable):
        self.exchanges.append({"exchange": exchange, "type": exchange_type, "durable": durable})

    def queue_declare(self, queue, durable, arguments=None):
        self.queues.append({"queue": queue, "durable": durable, "arguments": arguments})

    def queue_bind(self, queue, exchange, routing_key):
        self.bindings.append({"queue": queue, "exchange": exchange, "routing_key": routing_key})


def _settings(**overrides) -> Settings:
    defaults = dict(
        postgres_host="localhost",
        postgres_db="db",
        postgres_user="user",
        postgres_password="pw",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_declares_document_exchange_as_durable_direct():
    channel = FakeChannel()
    settings = _settings()

    declare_topology(channel, settings)

    assert channel.exchanges == [
        {"exchange": settings.rabbitmq_document_exchange, "type": "direct", "durable": True}
    ]


def test_declares_dlq_and_retry_queue_without_dead_letter_arguments():
    channel = FakeChannel()
    settings = _settings()

    declare_topology(channel, settings)

    dlq_and_retry = [q for q in channel.queues if q["queue"] in (settings.rabbitmq_dlq, settings.rabbitmq_retry_queue)]
    assert {q["queue"] for q in dlq_and_retry} == {settings.rabbitmq_dlq, settings.rabbitmq_retry_queue}
    assert all(q["arguments"] is None for q in dlq_and_retry)


def test_work_queues_declared_durable_with_dead_letter_routing_to_dlq():
    channel = FakeChannel()
    settings = _settings()

    declare_topology(channel, settings)

    work_queues = {settings.rabbitmq_process_queue, settings.rabbitmq_reindex_queue, settings.rabbitmq_delete_queue}
    declared = [q for q in channel.queues if q["queue"] in work_queues]
    assert {q["queue"] for q in declared} == work_queues
    for q in declared:
        assert q["durable"] is True
        assert q["arguments"] == {"x-dead-letter-exchange": "", "x-dead-letter-routing-key": settings.rabbitmq_dlq}


def test_work_queues_bound_to_document_exchange_with_matching_routing_keys():
    channel = FakeChannel()
    settings = _settings()

    declare_topology(channel, settings)

    assert {(b["queue"], b["routing_key"]) for b in channel.bindings} == {
        (settings.rabbitmq_process_queue, settings.rabbitmq_process_routing_key),
        (settings.rabbitmq_reindex_queue, settings.rabbitmq_reindex_routing_key),
        (settings.rabbitmq_delete_queue, settings.rabbitmq_delete_routing_key),
    }
    assert all(b["exchange"] == settings.rabbitmq_document_exchange for b in channel.bindings)
