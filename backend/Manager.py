import json
import os
from threading import Thread
from time import sleep

from PySide6.QtCore import Property, QObject, Signal, Slot

from backend.HandSegmentor import HandSegmentor
from backend.BackgroundImposing.filtration import Filtration
from backend.BackgroundImposing.generation_backs import BacksGeneration


class Manager(QObject):
    '''Class that manages the whole process of the program
    
    Args:
        QObject (PySide6.QtCore.QObject): QObject
    
    Attributes:
        name_list (list): list of names of people
        images_path (str): path to directory where images are saved
        empty_tables_directory (str): path to directory where empty tables are saved
        config (dict): config
        photo_num (int): number of photos to generate
        backsGenerationPercent (float): percent of backsGeneration
        camera_num (int): number of camera
        hsStatus (float): status of hand segmentation
    '''

    nameListChanged = Signal()
    imagesPathChanged = Signal()
    emptyTablePathChanged = Signal()
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
        self.emptyTablePathChanged.emit()
        self.hs = HandSegmentor(self._config)
        self.filter = Filtration(self._config)
        self.bg = BacksGeneration(self._config)
        self._photo_num = self._config['generation_backs']['photo_num']
        self._backsGenerationPercent = 0.
        self._camera_num = self._config["camera_num"]
        self._hsStatus = 0
        self._empty_tables_directory = self._config['empty_tables_directory']
        if not os.path.exists(self._images_path):
            os.mkdir(self._images_path)
        if not os.path.exists(self._empty_tables_directory):
            os.mkdir(self._empty_tables_directory)


    def __set_name_list(self, name_list):
        self._name_list = name_list
        self.nameListChanged.emit()


    def __get_name_list(self) -> list:
        return self._name_list


    @Slot("QVariant")
    def addName(self, name: str):
        '''Adds name to name_list and emits nameListChanged signal
        
        Args:
            name (str): name to add
        '''
        if name in self._name_list:
            self.nameListChanged.emit()
            return
        self._name_list.append(name)
        self.nameListChanged.emit()


    @Slot("QVariant", "QVariant")
    def changeName(self, index: int, name: str):
        '''Changes name in name_list by index and emits nameListChanged signal
        
        Args:
            index (int): index of name in name_list
            name (str): new name
        '''
        if name in self._name_list:
            self.nameListChanged.emit()
            return
        self._name_list[index] = name
        self.nameListChanged.emit()


    @Slot("QVariant")
    def removeName(self, name: str):
        '''Removes name from name_list and emits nameListChanged signal
        
        Args:
            name (str): name to remove
        '''
        if name not in self._name_list:
            self.nameListChanged.emit()
            return
        self._name_list.remove(name)
        self.nameListChanged.emit()


    @Slot("QVariant")
    def sleepFor(self, secs: float):
        '''Sleeps for secs seconds
        
        Args:
            secs (float): seconds to sleep
        '''
        sleep(secs)


    def __get_images_path(self) -> str:
        return os.path.abspath(self._images_path)


    def __set_images_path(self, path: str):
        self._images_path = path
        self.imagesPathChanged.emit()


    def __get_empty_tables_directory(self):
        return os.path.abspath(self._empty_tables_directory)


    def __set_empty_tables_directory(self, path: str):
        self._empty_tables_directory = path
        self.emptyTablePathChanged.emit()


    def __get_config(self):
        return self._config


    def __set_config(self, new_config: dict):
        self._config = new_config
        self.configChanged.emit()


    @Slot("QVariant")
    def makeDir(self, dirname: str):
        '''Creates directory with name dirname in images_path
        
        Args:
            dirname (str): name of directory to create
        '''
        if dirname in os.listdir(self.images_path):
            return
        os.mkdir(self.images_path + '/' + dirname)


    def increment_hsStatus(self, increment: float):
        '''Increments hsStatus by increment and emits hsStatusChanged signal
        
        Args:
            increment (float): increment
        '''
        self.hsStatus += increment


    @Slot()
    def handSegmentor(self):
        '''Call hand segmentor
        
        Creates a demon thread for hand segmentor and starts it
        '''
        self.hsStatus = 0
        Thread(target=self.hs.main_job,
               args=(self.hsEnded, self.increment_hsStatus),
               daemon=True).start()


    @Slot()
    def filtration(self):
        '''Call filtration'''
        self.filter.main_job()


    def backsGenerationStep(self):
        '''Emits backsGenerationPercentChanged signal'''
        for percent in self.bg.main_job(int(self.photo_num)):
            self.backsGenerationPercent = percent
        self.backsGenerationEnded.emit()


    @Slot()
    def backsGeneration(self):
        '''Call backs generation

        Creates a demon thread for backs generation and starts it
        '''
        self.backsGenerationPercent = 0
        Thread(target=self.backsGenerationStep, daemon=True).start()


    @Slot("QVariant")
    def __set_photo_num(self, photo_num: int):
        self._photo_num = photo_num
        self.photoNumChanged.emit()


    def __get_photo_num(self):
        return self._photo_num


    def __get_backsGenerationPercent(self):
        return self._backsGenerationPercent


    @Slot("QVariant")
    def __set_backsGenerationPercent(self, percent: float):
        self._backsGenerationPercent = percent
        self.backsGenerationPercentChanged.emit()


    def __get_camera_num(self):
        return self._camera_num


    @Slot("QVariant")
    def __set_camera_num(self, camera_num: int):
        self._camera_num = camera_num
        self.cameraNumChanged.emit()


    def __get_hsStatus(self) -> float:
        return self._hsStatus


    @Slot("QVariant")
    def __set_hsStatus(self, status: float):
        self._hsStatus = status
        self.hsStatusChanged.emit()


    name_list =                 Property("QVariantList",
                                         fget=__get_name_list,
                                         fset=__set_name_list,
                                         notify=nameListChanged)

    images_path =               Property("QVariant",
                                         fget=__get_images_path,
                                         fset=__set_images_path,
                                         notify=imagesPathChanged)

    config =                    Property("QJsonObject",
                                         fget=__get_config,
                                         fset=__set_config,
                                         notify=configChanged)

    photo_num =                 Property("QVariant",
                                         fget=__get_photo_num,
                                         fset=__set_photo_num,
                                         notify=photoNumChanged)

    camera_num =                Property("QVariant",
                                         fget=__get_camera_num,
                                         fset=__set_camera_num,
                                         notify=cameraNumChanged)

    backsGenerationPercent =    Property("QVariant",
                                         fget=__get_backsGenerationPercent,
                                         fset=__set_backsGenerationPercent,
                                         notify=backsGenerationPercentChanged)

    hsStatus =                  Property("QVariant",
                                         fget=__get_hsStatus,
                                         fset=__set_hsStatus,
                                         notify=hsStatusChanged)

    empty_tables_directory =    Property("QVariant",
                                         fget=__get_empty_tables_directory,
                                         fset=__set_empty_tables_directory,
                                         notify=emptyTablePathChanged)

