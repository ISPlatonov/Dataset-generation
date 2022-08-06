from PySide2.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot
import json


class Manager(QObject):
    #makeSnapshot = Signal()

    def __init__(self):
        super(Manager, self).__init__()
        with open('config.json', 'r') as f:
            self.config = json.load(f)
    
    
