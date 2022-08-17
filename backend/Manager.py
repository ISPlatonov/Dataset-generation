from tkinter import N
from PySide2.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot
import json, os
from time import sleep

from backend.HandSegmentor import HandSegmentor
from backend.BackgroundImposing.filtration import Filtration
from backend.BackgroundImposing.generation_backs import BacksGeneration


class Manager(QObject):
    #makeSnapshot = Signal()
    nameListChanged = Signal()
    imagesPathChanged = Signal()


    def __init__(self):
        super(Manager, self).__init__()
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        # for testing only!
        self._name_list = self.config['name_list']
        self.nameListChanged.emit()
        self._images_path = self.config['images_path']
        self.imagesPathChanged.emit()
        self.hs = HandSegmentor(self.config)
        self.filter = Filtration(self.config)
        self.bg = BacksGeneration(self.config)
    

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
            self.nameListChanged.emit()
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
            self.nameListChanged.emit()
            return
        self._name_list.remove(name)
        self.nameListChanged.emit()
    

    def get_images_path(self):
        return os.path.abspath(self._images_path)
    

    def set_images_path(self, path):
        self._images_path = path
        self.imagesPathChanged.emit()


    @Slot("QVariant")
    def makeDir(self, dirname):
        if dirname in os.listdir(self.get_images_path()):
            return
        os.mkdir(self.get_images_path() + '/' + dirname)
    

    @Slot()
    def handSegmentor(self):
        self.hs.main_job()
    

    @Slot()
    def filtration(self):
        self.filter.main_job()
    

    @Slot()
    def backsGeneration(self):
        self.bg.main_job()
    

    @Slot("QVariant")
    def sleepFor(self, secs):
        sleep(secs)

    
    name_list = Property("QVariantList", fget=get_name_list, fset=set_name_list, notify=nameListChanged)
    images_path = Property("QVariant", fget=get_images_path, fset=set_images_path, notify=imagesPathChanged)
