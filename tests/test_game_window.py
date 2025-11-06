import importlib


def load_game_window():
    module = importlib.import_module("game_window")
    return importlib.reload(module)


def test_compare_image_returns_expected_values(monkeypatch):
    game_window = load_game_window()

    def fake_match(template, image, method):
        return "fake_result"

    def fake_minmax(result):
        return 0.1, 0.95, (0, 0), (15, 25)

    monkeypatch.setattr(game_window.cv2, "matchTemplate", fake_match)
    monkeypatch.setattr(game_window.cv2, "minMaxLoc", fake_minmax)

    max_val, max_loc = game_window.compare_image("template", "image")

    assert max_val == 0.95
    assert max_loc == (15, 25)


def test_compare_image_handles_errors(monkeypatch):
    game_window = load_game_window()
    warnings = []

    class DummyLogger:
        def warning(self, message):
            warnings.append(message)

    def fake_match(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(game_window, "logger", DummyLogger())
    monkeypatch.setattr(game_window.cv2, "matchTemplate", fake_match)

    max_val, max_loc = game_window.compare_image("template", "image")

    assert max_val == 0
    assert max_loc == 0
    assert len(warnings) >= 2
