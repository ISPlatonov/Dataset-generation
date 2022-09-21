import sys
import signal

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from backend.Manager import Manager


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    manager = Manager()
    engine.rootContext().setContextProperty('manager', manager)

    engine.load('frontend/main.qml')

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())
