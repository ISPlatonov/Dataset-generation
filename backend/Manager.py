from tkinter import N
from PySide2.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot
import json


class Manager(QObject):
    #makeSnapshot = Signal()
    nameListChanged = Signal()

    def __init__(self):
        super(Manager, self).__init__()
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        # for testing only!
        self._name_list = self.config['name_list']
        self.nameListChanged.emit()
    
    #@Slot("QVariant")
    #def make_snapshots_step(self, name_list):
    #    msg = name_list.toVariant()
    
    def set_name_list(self, name_list):
        self._name_list = name_list
        self.nameListChanged.emit()
    
    def get_name_list(self):
        return self._name_list
    
    @Slot("QVariant")
    def addName(self, name):
        if name in self._name_list:
            return
        self._name_list.append(name)
        self.nameListChanged.emit()
    
    @Slot("QVariant", "QVariant")
    def changeName(self, index, name):
        if name in self._name_list:
            self.nameListChanged.emit()
            return
        self._name_list[index] = name
        self.nameListChanged.emit()
    
    @Slot("QVariant")
    def removeName(self, name):
        if name not in self._name_list:
            return
        self._name_list.remove(name)
        self.nameListChanged.emit()
    
    name_list = Property("QVariantList", fget=get_name_list, fset=set_name_list, notify=nameListChanged)
