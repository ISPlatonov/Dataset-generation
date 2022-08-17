from PySide2.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide2.QtWidgets import QApplication, QListView
from PySide2.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot

import json, sys, signal, time, re, sys

from backend.Manager import Manager


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    engine = QQmlApplicationEngine()

    manager = Manager()
    engine.rootContext().setContextProperty('manager', manager)

    engine.load('frontend/main.qml')
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())