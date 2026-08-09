import json

from infrastructure.rabbitmq.consumer import consume_queue, consume_queues
from src.shared.config import Settings


class FakeMethod:
    def __init__(self, delivery_tag: int):
        self.delivery_tag = delivery_tag


class FakeChannel:
    def __init__(self):
        self.qos = None
        self.consumed_queue = None
        self.on_message = None
        self.consumed = {}
        self.acks: list[int] = []
        self.nacks: list[tuple[int, bool]] = []

    def basic_qos(self, prefetch_count):
        self.qos = prefetch_count

    def basic_consume(self, queue, on_message_callback):
        self.consumed_queue = queue
        self.on_message = on_message_callback
        self.consumed[queue] = on_message_callback

    def basic_ack(self, delivery_tag):
        self.acks.append(delivery_tag)

    def basic_nack(self, delivery_tag, requeue):
        self.nacks.append((delivery_tag, requeue))

    def start_consuming(self):
        pass  # test drives on_message directly instead of blocking

    def stop_consuming(self):
        pass


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
        rabbitmq_prefetch_count=5,
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def _run_consume(monkeypatch, handler):
    channel = FakeChannel()
    connection = FakeConnection(channel)
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.get_settings", lambda: _settings())
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.get_connection", lambda: connection)
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.declare_topology", lambda channel, settings: None)

    consume_queue("rag.document.processing", handler)
    return channel, connection


def test_consume_queue_applies_configured_prefetch_and_binds_to_requested_queue(monkeypatch):
    channel, connection = _run_consume(monkeypatch, lambda payload: None)

    assert channel.qos == 5
    assert channel.consumed_queue == "rag.document.processing"
    assert connection.closed is True


def test_on_message_acks_and_passes_decoded_payload_to_handler_on_success(monkeypatch):
    received = []
    channel, _ = _run_consume(monkeypatch, lambda payload: received.append(payload))

    channel.on_message(channel, FakeMethod(delivery_tag=1), None, json.dumps({"document_id": "abc"}).encode())

    assert received == [{"document_id": "abc"}]
    assert channel.acks == [1]
    assert channel.nacks == []


def test_on_message_nacks_without_requeue_when_handler_raises(monkeypatch):
    def failing_handler(payload):
        raise RuntimeError("boom")

    channel, _ = _run_consume(monkeypatch, failing_handler)

    channel.on_message(channel, FakeMethod(delivery_tag=7), None, json.dumps({}).encode())

    assert channel.nacks == [(7, False)]
    assert channel.acks == []


def test_on_message_nacks_without_requeue_on_malformed_json(monkeypatch):
    channel, _ = _run_consume(monkeypatch, lambda payload: None)

    channel.on_message(channel, FakeMethod(delivery_tag=3), None, b"not json")

    assert channel.nacks == [(3, False)]
    assert channel.acks == []


def test_consume_queues_binds_each_queue_to_its_own_handler(monkeypatch):
    channel = FakeChannel()
    connection = FakeConnection(channel)
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.get_settings", lambda: _settings())
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.get_connection", lambda: connection)
    monkeypatch.setattr("infrastructure.rabbitmq.consumer.declare_topology", lambda channel, settings: None)

    reindex_received, delete_received = [], []
    consume_queues(
        {
            "rag.document.reindex": lambda payload: reindex_received.append(payload),
            "rag.document.delete": lambda payload: delete_received.append(payload),
        }
    )

    assert set(channel.consumed.keys()) == {"rag.document.reindex", "rag.document.delete"}

    channel.consumed["rag.document.reindex"](channel, FakeMethod(1), None, json.dumps({"a": 1}).encode())
    channel.consumed["rag.document.delete"](channel, FakeMethod(2), None, json.dumps({"b": 2}).encode())

    assert reindex_received == [{"a": 1}]
    assert delete_received == [{"b": 2}]
    assert channel.acks == [1, 2]
