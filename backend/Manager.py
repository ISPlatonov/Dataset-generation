import json
import os
from threading import Thread
from time import sleep
from locale import atof 

from PySide6.QtCore import Property, QObject, Signal, Slot

from backend.HandSegmentor import HandSegmentor
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
        iou (double): the value of IoU for generation photos
        backsGenerationPercent (float): percent of backsGeneration
        camera_num (int): number of camera
        hsStatus (float): status of hand segmentation
    '''

    nameListChanged = Signal()
    imagesPathChanged = Signal()
    emptyTablePathChanged = Signal()
    configChanged = Signal()
    snapshotsNumberChanged = Signal()
    processedPathChanged = Signal()
    backgroundsPathChanged = Signal()
    rawPhotosPathChanged = Signal()
    generatedPathChanged = Signal()
    snapshotDelayChanged = Signal()
    photoNumChanged = Signal()
    backsGenerationPercentChanged = Signal()
    cameraNumChanged = Signal()
    hsEnded = Signal()
    hsStatusChanged = Signal()
    backsGenerationEnded = Signal()
    iouChanged = Signal()
    maxNumberChanged = Signal()
    maskIndicatorChanged = Signal()
    roiIndicatorChanged = Signal()
    staticIndicatorChanged = Signal()
    configChanged = Signal()
    handIndicatorChanged = Signal()
    rectangleIndicatorChanged = Signal()
    numberOfMasksChanged = Signal()
    numberHandsChanged = Signal()


    def __init__(self):
        super(Manager, self).__init__()
        with open('config.json', 'r') as f:
            self._config = json.load(f)
        
        # For 1 step:
        self._snapshots_number = self._config['snapshots']['snapshots_number']
        self._raw_photos_path = self._config['1_step']['raw_photos_path']
        self._snapshot_delay = self._config['snapshots']['snapshot_delay']
        
        # For the 2 step:
        self._processed_path = self._config['preprocessing']['processed_folder']
        self._roi_indicator = self._config['preprocessing']['roi_indicator'] 
        self._mask_indicator = self._config['preprocessing']['mask_indicator'] 
        self._hand_indicator = self._config['preprocessing']['hand_indicator']

        # For the 3 step:
        self._backgrounds_path = self._config['generation_backs']['backgrounds']
        self._generated_path = self._config['generation_backs']['generation_folder']

        # Others:
        self._name_list = self._config['name_list']
        self.nameListChanged.emit()
        self._images_path = self._config['1_step']['raw_photos_path']
        self.imagesPathChanged.emit()   # зачем?  good taste?
        self.emptyTablePathChanged.emit()
        

        self.hs = HandSegmentor(self._config)
        self.bg = BacksGeneration(self._config)

        self._iou = self._config['generation_backs']['iou']
        self._max_hands_on_photo = self._config['generation_backs']['max_hands_on_photo']
        self._rectangle_indicator = self._config['generation_backs']['rectangle_indicator']
        self._max_details_on_photo = self._config['generation_backs']['max_details_on_photo']
        self._backsGenerationPercent = 0.
        self._camera_num = self._config["camera_num"]
        self._hsStatus = 0
        if not os.path.exists(self._processed_path):
            os.mkdir(self._processed_path)
        self._number_of_masks = self.count_masks() 
        self.get_mask_folders() 
        self.get_hand_folders()

        self._photo_num = int(self._number_of_masks * 4 / (self._max_details_on_photo / 2))  
        if not os.path.exists(self._images_path):
            os.mkdir(self._images_path)

    def count_masks(self):
        count = 0
        for dir in os.listdir(self._processed_path):
            if os.path.exists(self._processed_path + "/" + dir + "/" + dir + "_roi.jpg"):
                count += 1
        self._config['generation_backs']['number_of_masks'] = count
        return count

    def count_hands(self):
        count = 0
        for dir in os.listdir(self._processed_path):
            if os.path.exists(self._processed_path + "/" + dir + "/" + dir + "_continious_hand_bw_mask.jpg"):
                count += 1
        self._config['generation_backs']['number_of_hand_masks'] = count
        return count


    def get_mask_folders(self):
        self._config['generation_backs']['all_mask_folders'] = []
        for dir in os.listdir(self._processed_path):
            if os.path.exists(self._processed_path + dir + "/" + dir + "_roi.jpg"):
                self._config['generation_backs']['all_mask_folders'].append(dir)
        return self._config['generation_backs']['all_mask_folders']


    def get_hand_folders(self):
        self._config['generation_backs']['all_hand_folders'] = []
        for dir in os.listdir(self._processed_path):
            if os.path.exists(self._processed_path + dir + "/" + dir + "_continious_hand_bw_mask.jpg"):
                self._config['generation_backs']['all_hand_folders'].append(dir)
        return self._config['generation_backs']['all_hand_folders']


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
               args=(self.hsEnded, self.increment_hsStatus, self._config),
               daemon=True).start()


    @Slot()
    def backsGenerationStep(self):
        '''Emits backsGenerationPercentChanged signal'''
        for percent in self.bg.main_job(self._config):
            self.backsGenerationPercent = percent
        self.backsGenerationEnded.emit()


    @Slot()
    def backsGeneration(self):
        '''Call backs generation

        Creates a demon thread for backs generation and starts it
        '''
        self.backsGenerationPercent = 0
        Thread(target=self.backsGenerationStep, daemon=True).start()

    # For 1 step:

    @Slot("QVariant")
    def __set_snapshots_number(self, snapshots_number: int):
        self._snapshots_number = snapshots_number
        self.snapshotsNumberChanged.emit()


    def __get_snapshots_number(self):
        return self._snapshots_number


    @Slot("QVariant")
    def __set_raw_photos_path(self, path: str):
        self._raw_photos_path = path
        self._config['1_step']['raw_photos_path'] = path
        self.rawPhotosPathChanged.emit()


    def __get_raw_photos_path(self):
        return self._raw_photos_path

    
    @Slot("QVariant")
    def __set_snapshot_delay(self, snapshot_delay):
        snapshot_delay = snapshot_delay.replace(',', '.')
        self._snapshot_delay = atof(snapshot_delay)
        self._config['snapshots']['snapshot_delay'] = self._snapshot_delay
        self.snapshotDelayChanged.emit()

    def __get_snapshot_delay(self):
        return self._snapshot_delay


    # For 2 step:
    @Slot("QVariant")
    def __set_processed_path(self, path: str):
        self._processed_path = path
        self._config['preprocessing']['processed_folder'] = path
        self.processedPathChanged.emit()


    def __get_processed_path(self):
        return self._processed_path


    @Slot("QVariant")
    def __set_roi_indicator(self, roi_indicator: int):
        self._roi_indicator = roi_indicator
        self._config['preprocessing']['roi_indicator'] = roi_indicator
        self.roiIndicatorChanged.emit()


    def __get_roi_indicator(self):
        return self._roi_indicator


    @Slot("QVariant")
    def __set_mask_indicator(self, mask_indicator: int):
        self._mask_indicator = mask_indicator
        self._config['preprocessing']['mask_indicator'] = mask_indicator
        self.maskIndicatorChanged.emit()


    def __get_mask_indicator(self):
        return self._mask_indicator


    @Slot("QVariant")
    def __set_hand_indicator(self, hand_indicator: int):
        self._hand_indicator = hand_indicator
        self._config['preprocessing']['hand_indicator'] = hand_indicator
        self.handIndicatorChanged.emit()


    def __get_hand_indicator(self):
        return self._hand_indicator


    # For 3 step:
    @Slot("QVariant")
    def __set_backgrounds_path(self, path: str):
        self._backgrounds_path = path
        self._config['generation_backs']['backgrounds'] = path
        self.backgroundsPathChanged.emit()


    def __get_backgrounds_path(self):
        return self._backgrounds_path


    @Slot("QVariant")
    def __set_generated_path(self, path: str):
        self._generated_path = path
        self._config['generation_backs']['generation_folder'] = path
        self.generatedPathChanged.emit()


    def __get_generated_path(self):
        return self._generated_path


    @Slot("QVariant")
    def __set_photo_num(self, photo_num: int):
        self._photo_num = photo_num
        self._config['generation_backs']['photo_num'] = photo_num
        self.photoNumChanged.emit()


    def __get_photo_num(self):
        return self._photo_num


    @Slot("QVariant")
    def __set_max_details_on_photo(self, max_details_on_photo):
        self._max_details_on_photo = float(max_details_on_photo)
        self._config['generation_backs']['max_details_on_photo'] = int(max_details_on_photo)
        self.maxNumberChanged.emit()


    def __get_max_details_on_photo(self):
        return self._max_details_on_photo


    @Slot("QVariant")
    def __set_iou(self, iou):
        iou = iou.replace(',', '.')
        self._iou = atof(iou)
        self._config['generation_backs']['iou'] = self._iou
        self.iouChanged.emit()


    def __get_iou(self):
        return self._iou


    @Slot("QVariant")
    def __set_number_of_masks(self, number_of_masks):
        self._number_of_masks = number_of_masks
        self.numberOfMasksChanged.emit()


    def __get_number_of_masks(self):
        return self._number_of_masks
    

    @Slot("QVariant")
    def __set_max_hands_on_photo(self, max_hands_on_photo: int):
        self._max_hands_on_photo = int(max_hands_on_photo)
        self._config['generation_backs']['max_hands_on_photo'] = int(max_hands_on_photo)
        self.handIndicatorChanged.emit()


    def __get_max_hands_on_photo(self):
        return self._max_hands_on_photo


    @Slot("QVariant")
    def __set_rectangle_indicator(self, rectangle_indicator: int):
        self._rectangle_indicator = rectangle_indicator
        self._config['generation_backs']['rectangle_indicator'] = rectangle_indicator
        self.rectangleIndicatorChanged.emit()


    def __get_rectangle_indicator(self):
        return self._rectangle_indicator


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

    # For 1 step:                               
    snapshots_number =          Property("QVariant",
                                         fget=__get_snapshots_number,
                                         fset=__set_snapshots_number,
                                         notify=snapshotsNumberChanged)
    

    snapshots_delay =                       Property("QVariant",
                                         fget=__get_snapshot_delay,
                                         fset=__set_snapshot_delay,
                                         notify=snapshotDelayChanged)

    # For 2 step
    mask_indicator =            Property("QVariant",
                                         fget=__get_mask_indicator,
                                         fset=__set_mask_indicator,
                                         notify=maskIndicatorChanged)

    roi_indicator =             Property("QVariant",
                                         fget=__get_roi_indicator,
                                         fset=__set_roi_indicator,
                                         notify=roiIndicatorChanged)

    processed_path =            Property("QVariant",
                                         fget=__get_processed_path,
                                         fset=__set_processed_path,
                                         notify=processedPathChanged)

    hand_indicator =            Property("QVariant",
                                         fget=__get_hand_indicator,
                                         fset=__set_hand_indicator,
                                         notify=handIndicatorChanged)                                   
                                         
    # For 3 step
    backgrounds_path =          Property("QVariant",
                                         fget=__get_backgrounds_path,
                                         fset=__set_backgrounds_path,
                                         notify=backgroundsPathChanged)

    raw_photos_path =           Property("QVariant",
                                         fget=__get_raw_photos_path,
                                         fset=__set_raw_photos_path,
                                         notify=rawPhotosPathChanged)

    generated_path =            Property("QVariant",
                                         fget=__get_generated_path,
                                         fset=__set_generated_path,
                                         notify=generatedPathChanged)
                                         
    photo_num =                 Property("QVariant",
                                         fget=__get_photo_num,
                                         fset=__set_photo_num,
                                         notify=photoNumChanged)
 
    max_details_on_photo =      Property("QVariant",
                                         fget=__get_max_details_on_photo,
                                         fset=__set_max_details_on_photo,
                                         notify=maxNumberChanged)

    iou =                       Property("QVariant",
                                         fget=__get_iou,
                                         fset=__set_iou,
                                         notify=iouChanged)

    number_of_masks =           Property("QVariant",
                                         fget=__get_number_of_masks,
                                         fset=__set_number_of_masks,
                                         notify=numberOfMasksChanged)

    max_hands_on_photo =        Property("QVariant",
                                         fget=__get_max_hands_on_photo,
                                         fset=__set_max_hands_on_photo,
                                         notify=handIndicatorChanged)

    rectangle_indicator =       Property("QVariant",
                                         fget=__get_rectangle_indicator,
                                         fset=__set_rectangle_indicator,
                                         notify=rectangleIndicatorChanged)
                                    
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
