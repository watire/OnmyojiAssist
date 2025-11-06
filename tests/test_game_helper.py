import importlib
import logging


def load_game_helper():
    module = importlib.import_module("game_helper")
    return importlib.reload(module)


def test_init_logger_configures_handlers(monkeypatch):
    game_helper = load_game_helper()
    test_logger = logging.getLogger("test_init_logger_configures_handlers")
    test_logger.handlers = []
    test_logger.setLevel(logging.WARNING)
    monkeypatch.setattr(game_helper, "logger", test_logger, raising=False)

    game_helper.init_logger()

    try:
        assert test_logger.level == logging.INFO
        assert any(isinstance(handler, logging.StreamHandler) for handler in test_logger.handlers)
        assert any(isinstance(handler, game_helper.MyQtHandler) for handler in test_logger.handlers)
    finally:
        for handler in list(test_logger.handlers):
            test_logger.removeHandler(handler)


def test_myqt_handler_emit_writes_to_xstream(monkeypatch):
    game_helper = load_game_helper()

    collected_messages = []

    class DummyStream:
        def write(self, message):
            collected_messages.append(message)

    dummy_stream = DummyStream()
    monkeypatch.setattr(game_helper.XStream, "stdout", staticmethod(lambda: dummy_stream))

    handler = game_helper.MyQtHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg="hello world",
        args=(),
        exc_info=None,
    )

    handler.emit(record)

    assert collected_messages == ["hello world"]
