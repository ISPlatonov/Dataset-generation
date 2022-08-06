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
    
    name_list = Property("QVariantList", fget=get_name_list, fset=set_name_list, notify=nameListChanged)
