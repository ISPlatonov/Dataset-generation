from PySide6.QtCore import Property, QCoreApplication, QObject, Qt, Signal, QStringListModel, QJsonValue, Slot
import json, os
from time import sleep
from threading import Thread

from backend.HandSegmentor import HandSegmentor
from backend.BackgroundImposing.filtration import Filtration
from backend.BackgroundImposing.generation_backs import BacksGeneration


class Manager(QObject):
    #makeSnapshot = Signal()
    nameListChanged = Signal()
    imagesPathChanged = Signal()
    configChanged = Signal()
    photoNumChanged = Signal()
    backsGenerationPercentChanged = Signal()
    cameraNumChanged = Signal()
    hsEnded = Signal()
    hsStatusChanged = Signal()
    backsGenerationEnded = Signal()


    def __init__(self):
        super(Manager, self).__init__()
        with open('config.json', 'r') as f:
            self._config = json.load(f)
        # for testing only!
        self._name_list = self._config['name_list']
        self.nameListChanged.emit()
        self._images_path = self._config['images_path']
        self.imagesPathChanged.emit()
        self.hs = HandSegmentor(self._config)
        self.filter = Filtration(self._config)
        self.bg = BacksGeneration(self._config)
        self._photo_num = self._config['photo_num']
        self._backsGenerationPercent = 0.
        self._camera_num = self._config["camera_num"]
        self._hsStatus = 0.
    

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
    

    def get_config(self):
        return self._config
    

    def set_config(self, new_config):
        self._config = new_config
        self.configChanged.emit()


    @Slot("QVariant")
    def makeDir(self, dirname):
        if dirname in os.listdir(self.get_images_path()):
            return
        os.mkdir(self.get_images_path() + '/' + dirname)
    

    def increment_hsStatus(self, increment):
        self.hsStatus += increment


    @Slot()
    def handSegmentor(self):
        self.set_hsStatus(0.)
        #Thread(target=self.hs.main_job, args=(self.hsEnded,)).start()
        Thread(target=self.hs.main_job, args=(self.hsEnded, self.increment_hsStatus), daemon=True).start()
    

    @Slot()
    def filtration(self):
        self.filter.main_job()
    

    def backsGenerationStep(self):
        for percent in self.bg.main_job(int(self.photo_num)):
            print(f'backsGeneration percent: {percent}')
            self.set_backsGenerationPercent(percent)
        self.backsGenerationEnded.emit()


    @Slot()
    def backsGeneration(self):
        self.set_backsGenerationPercent(0.)
        Thread(target=self.backsGenerationStep, daemon=True).start()
    

    @Slot("QVariant")
    def set_photo_num(self, photo_num):
        self._photo_num = photo_num
        self.photoNumChanged.emit()
    

    #@Slot()
    def get_photo_num(self):
        return self._photo_num
    

    @Slot("QVariant")
    def sleepFor(self, secs):
        sleep(secs)


    def get_backsGenerationPercent(self):
        return self._backsGenerationPercent
    

    @Slot("QVariant")
    def set_backsGenerationPercent(self, percent):
        self._backsGenerationPercent = percent
        self.backsGenerationPercentChanged.emit()
    

    def get_camera_num(self):
        return self._camera_num
    

    @Slot("QVariant")
    def set_camera_num(self, camera_num):
        self._camera_num = camera_num
        self.cameraNumChanged.emit()
    

    def get_hsStatus(self):
        return self._hsStatus
    

    @Slot("QVariant")
    def set_hsStatus(self, status):
        self._hsStatus = status
        self.hsStatusChanged.emit()
    
    
    name_list = Property("QVariantList", fget=get_name_list, fset=set_name_list, notify=nameListChanged)
    images_path = Property("QVariant", fget=get_images_path, fset=set_images_path, notify=imagesPathChanged)
    config = Property("QJsonObject", fget=get_config, fset=set_config, notify=configChanged)
    photo_num = Property("QVariant", fget=get_photo_num, fset=set_photo_num, notify=photoNumChanged)
    camera_num = Property("QVariant", fget=get_camera_num, fset=set_camera_num, notify=cameraNumChanged)
    backsGenerationPercent = Property("QVariant", fget=get_backsGenerationPercent, fset=set_backsGenerationPercent, notify=backsGenerationPercentChanged)
    hsStatus = Property("QVariant", fget=get_hsStatus, fset=set_hsStatus, notify=hsStatusChanged)
