import logging

import src.shared.logging as logging_module
from src.shared.logging import get_logger


def test_get_logger_returns_logger_with_requested_name(monkeypatch):
    monkeypatch.setattr(logging_module, "_configured", False)

    logger = get_logger("my.module")

    assert logger.name == "my.module"
    assert isinstance(logger, logging.Logger)


def test_get_logger_only_configures_root_logging_once(monkeypatch):
    monkeypatch.setattr(logging_module, "_configured", False)
    calls = []
    monkeypatch.setattr(logging_module.logging, "basicConfig", lambda **kwargs: calls.append(kwargs))

    get_logger("a")
    get_logger("b")

    assert len(calls) == 1
