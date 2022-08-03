from PySide2.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide2.QtWidgets import QApplication, QListView
from PySide2.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot

import json, sys, signal, time, re, sys


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    engine = QQmlApplicationEngine()

    #manager = Manager()
    #engine.rootContext().setContextProperty('manager', manager)

    #mqtt_deamon = MQTT_Deamon(manager.config["mqtt_broker"]["address"], manager.config["mqtt_broker"]["port"], {})
    #manager.add_mqtt_publisher(mqtt_deamon)

    engine.load('main.qml')
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())