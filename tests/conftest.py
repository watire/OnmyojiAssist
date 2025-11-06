import sys
import types
import pytest


@pytest.fixture(autouse=True)
def stub_external_dependencies():
    created_modules = {}

    if "PyQt5" not in sys.modules:
        pyqt5_module = types.ModuleType("PyQt5")
        qtcore_module = types.ModuleType("PyQt5.QtCore")
        qtwidgets_module = types.ModuleType("PyQt5.QtWidgets")

        class DummySignal:
            def __init__(self, *args, **kwargs):
                self._callbacks = []

            def connect(self, callback):
                self._callbacks.append(callback)

            def emit(self, *args, **kwargs):
                for callback in list(self._callbacks):
                    callback(*args, **kwargs)

        class DummyQObject:
            def __init__(self, *args, **kwargs):
                pass

            def signalsBlocked(self):
                return False

        class DummyQTimer(DummyQObject):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._interval = None
                self.timeout = DummySignal()

            def setInterval(self, interval):
                self._interval = interval

            def start(self):
                pass

            def stop(self):
                pass

        class DummyMessageBox:
            def __init__(self, *args, **kwargs):
                self.window_title = ""
                self.text_value = ""

            def setWindowTitle(self, title):
                self.window_title = title

            def setText(self, text):
                self.text_value = text

            def hide(self):
                pass

        qtcore_module.QObject = DummyQObject
        qtcore_module.QTimer = DummyQTimer
        qtcore_module.pyqtSignal = DummySignal
        qtwidgets_module.QMessageBox = DummyMessageBox

        pyqt5_module.QtCore = qtcore_module
        pyqt5_module.QtWidgets = qtwidgets_module

        created_modules["PyQt5"] = pyqt5_module
        created_modules["PyQt5.QtCore"] = qtcore_module
        created_modules["PyQt5.QtWidgets"] = qtwidgets_module

    for name in ("win32gui", "win32ui", "win32con"):
        if name not in sys.modules:
            created_modules[name] = types.ModuleType(name)

    if "numpy" not in sys.modules:
        numpy_module = types.ModuleType("numpy")

        def fromstring(data, dtype="uint8"):
            return data

        numpy_module.fromstring = fromstring
        created_modules["numpy"] = numpy_module

    if "cv2" not in sys.modules:
        cv2_module = types.ModuleType("cv2")
        cv2_module.TM_CCOEFF_NORMED = 5
        created_modules["cv2"] = cv2_module

    sys.modules.update(created_modules)

    try:
        yield
    finally:
        for name in created_modules:
            sys.modules.pop(name, None)
