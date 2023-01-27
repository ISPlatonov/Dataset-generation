from pyclbr import Function
from typing import Generator, Iterable
import cv2
import mediapipe as mp
import os
import numpy as np
import json
from PIL import ImageStat
import PIL
from pycocotools.coco import COCO
from threading import Thread, active_count
from PySide6.QtCore import Signal
from backend.BackgroundImposing.paths import *
from backend.BackgroundImposing.dict4json import Dict4Json
from backend.BackgroundImposing.augmentations import *
import torch
import pandas as pd


class HandSegmentor:

    def __init__(self, config: dict):
        self.root_dir_with_dirs = config["filepath"] 
        self.min_roi_height = config["roi"]["height"]
        self.min_roi_width = config["roi"]["width"]
        self.yolo_classificator_weigths_path = config["yolo_classificator_weigths_path"]
        self.yolo_repo_path = config["yolo_repo_path"]
        self.max_num_hands = config["mediapipe"]["max_num_hands"]
        self.min_detection_confidence = config['mediapipe']['min_detection_confidence']



    def find_detail_on_photo_yolo(self, yolo_classificator_weigths_path, yolo_repo_path, img_path):
        """
        Функция определяющая с помощью преобученной нейросети деталь / не деталь прямоугольник, 
        в котором находится деталь
        :param yolo_classificator_weigths_path: путь к весам модели
        :param yolo_repo_path: путь к клонированной с github папке yolov5
        :param img_path: путь к изображению, которое надо обработать

        :return x_min, x_max, y_min, y_max: координаты прямоугольника с деталью внутри
        """
        model = torch.hub.load(yolo_repo_path, 'custom', path=yolo_classificator_weigths_path, source='local')
        results = model([img_path])
        rect_dataframe = pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])
        for item in results.pandas().xyxy:
            rect_dataframe = pd.concat([rect_dataframe, item], ignore_index=True)
        if rect_dataframe.shape[0] != 0:
            rect_dataframe.sort_values(by='confidence', ascending=False)
            model_predicted_data = rect_dataframe.values[0]
            x_min, x_max = int(model_predicted_data[0]), int(model_predicted_data[2])
            y_min, y_max = int(model_predicted_data[1]), int(model_predicted_data[3])
            return x_min, x_max, y_min, y_max
        else: 
            return None


    def batch(self, iterable: Iterable, n=1) -> Generator[Iterable, None, None]:
        '''Divides the iterable into batches of size n

        Args:
            iterable (iterable): Iterable to divide
            n (int, optional): Size of the batches. Defaults to 1.
        
        Yields:
            iterable: Batch of size n
        '''
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
            

    def get_approx(self, black_and_white_mask, detail_name):
        """
        Функция получение аппроксимирующего контура.
        :param black_and_white_mask: array
        :return: array
        """
        mask_gray = black_and_white_mask
        mask_gray = cv2.bilateralFilter(mask_gray, 11, 17, 17)
        cnts, _ = cv2.findContours(mask_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # or cv2.RETR_TREE
        if len(cnts) == 0:
            return np.nan
        cnts = sorted(cnts, key=cv2.contourArea, reverse=False)[:]  # Отсортировали контуры по площади контура
                                                                        # и выбрали 10 самых больших.
        for c in cnts:
            peri = cv2.arcLength(c, True)  # Периметр замкнутых контуров
            approx = cv2.approxPolyDP(c, 0.005 * peri, True)  # Чем коэффициент перед peri больше, тем больше "сравнивание" границ.
                                                            # При 0.15 уже может получится квадрат из исходного множества
                                                            # точек, аппроксимирующих шестеренку, в cnts.
        return approx

    def get_yolo_points(self, points):
        """
        Функция получения из множества точек, приближающих изображение,
        двух, которые заключат фигуру в прямоугольник.
        :param points: array
        :return:
        """
        x, y = [], []
        for i in range(points.shape[0]):
            x.append((points[:][i][0])[0])  # выделили только х из переданного массива
            y.append((points[:][i][0])[1])  # выделили только у из переданного массива
        arr_x, arr_y = [], []
        for i in x:
            arr_x.append(int(i))
        x = arr_x
        for i in y:
            arr_y.append(int(i))
        y = arr_y
        yolo_points = [int(min(x)), int(min(y)), int(max(x)), int(max(y))]
        return yolo_points


    def get_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    
    def create_yolo_for_validation(self, file_name, points, category_id, dir_name):
        yolo_width = 4096.0 
        yolo_height = 2160.0
        try:
            os.mkdir(dir_name)
        except FileExistsError:
            pass
        f = open(f'{dir_name}/{file_name}.txt', 'w+')
        x_min = points[0]
        x_max = points[1]
        yolo_x = (x_max + x_min) / (yolo_width * 2)
        yolo_w = (x_max - x_min) / (yolo_width)

        y_min = points[2]
        y_max = points[3]
        yolo_y = (y_max + y_min) / (yolo_height * 2)
        yolo_h = (y_max - y_min) / (yolo_height)
        string = f'{category_id} {yolo_x} {yolo_y} {yolo_w} {yolo_h}\n'
        f.write(string)
        f.close()


    def preprocessing_with_nn(self, config_dict, filepath, filename, output_dir,
                            increment_hsStatus, increment, eps=200, show=False, save=True, need_hand=True):
        image_name = filename[:-4] 
        img = cv2.imread(filepath) 
        img_original = img.copy()
        folder_name_path = output_dir + '{}'.format(image_name)

        points = self.find_detail_on_photo_yolo(self.yolo_classificator_weigths_path, 
                                                               self.yolo_repo_path, 
                                                               filepath)
        if points != None:
            if (abs(points[0] - points[1]) > img_original.shape[1] / 2) or \
                (abs(points[2] - points[3]) > img_original.shape[0] / 2):
                return None
            roi = img_original[points[2]:points[3], points[0]:points[1]]
        else:
            return None  

        if config_dict['preprocessing']['make_validation_dataset'] == 1:
            folder_name = config_dict['preprocessing']['val_folder']
            directory_name = config_dict['preprocessing']['val_points_folder']
            img_resized = resize_specific_width_and_height(img, config_dict['preprocessing']['val_width'], config_dict['preprocessing']['val_height'])
            cv2.imwrite(f'{folder_name}/img_{len(os.listdir(folder_name))}.jpg', img_resized)
            category_id = self.labels.index(filename[:filename.rfind("_")])
            print(f'labels: {self.labels}\nfilename: {filename.rfind("_")}\nid:{category_id}\n')
            self.create_yolo_for_validation(f'img_{len(os.listdir(folder_name))}', points, category_id, directory_name)
            
        
        try:
            os.makedirs(folder_name_path)
        except OSError as e:
            pass

        cv2.imwrite(folder_name_path + '/{}.jpg'.format(image_name), img_original)
       
        if config_dict['preprocessing']['roi_indicator']:
            cv2.imwrite(folder_name_path + '/{}_roi.jpg'.format(image_name), roi)
       
        if config_dict['preprocessing']['hand_indicator']:
            self.getting_hand(config_dict, filename)

        if config_dict['preprocessing']['mask_indicator']:
            self.getting_mask(config_dict, filename, roi, points)


        increment_hsStatus(increment)
        return points

    def getting_hand(self, config_dict, filename):
        image_name = filename[:-4]
        processed_path = config_dict['preprocessing']['processed_folder'] 
        folder_name_path = processed_path + image_name + '/'
        x_landmark_coord, y_landmark_coord = [], []
        if os.path.exists(processed_path + image_name + "/" + filename):
            raw_photo_path = processed_path + image_name + "/" + filename
        else:
            print("Error in paths")
            return
        img = cv2.imread(raw_photo_path) 
        img_original = img.copy()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mpHands = mp.solutions.hands  # объект класса для распознавания рук на фотографии
        hands = mpHands.Hands(max_num_hands=self.max_num_hands, min_detection_confidence=self.min_detection_confidence)
        mpDraw = mp.solutions.drawing_utils  # рисуем метки кисти рук
        results = hands.process(imgRGB)  # process the tracking and return the results (landmarks and connections for hand)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:  # take all the landmarks for our hand(s)
                # next cycle for getting specific landmarks (x,y) and their id (they are already sorted)
                for id, lm in enumerate(handLms.landmark):
                    # the landmarks are returned as the ratio of the image (decimal values - not pixels) => convert them:
                    h, w, c = img.shape
                    # next coordinates of the center of all the landmarks (converted to pixels)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    x_landmark_coord.append(cx)
                    y_landmark_coord.append(cy)
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)  # отрисовываем скелет кисти руки
        else:
            hands.close()  # чистим память
            print("mediapipe error")
            return

        x_max, y_max, x_min, y_min = max(x_landmark_coord), max(y_landmark_coord), min(x_landmark_coord), min(
            y_landmark_coord)  # вписываем кисть в прямоугольник
        w, h = x_max - x_min, y_max - y_min
        eps = int(max(w, h) * 0.2)
        x_max, y_max, x_min, y_min = x_max + eps, y_max + eps, x_min - eps, y_min - eps  # отступаем от краев
        hands.close()  # чистим память
        hand_roi = img_original[y_min:y_max, x_min:x_max]
        cv2.imwrite(folder_name_path + '{}_hand_roi.jpg'.format(image_name), hand_roi)
        YCrCb = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2YCR_CB)  # преобразуем в пространство YCrCb
        (y, cr, cb) = cv2.split(YCrCb)  # выделяем значения Y, Cr, Cb
        cr1 = cv2.GaussianBlur(cr, (5, 5), 0)  # фильтр Гаусса для небольшого размытия
        _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # ostuprocessing
        res = cv2.bitwise_and(hand_roi, hand_roi, mask=skin)
        skin_color = res.copy()
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        dst = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
        Laplacian = cv2.convertScaleAbs(dst)
        h = cv2.findContours(Laplacian, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # находим на изображении контуры
        contour = h[0]
        contour = sorted(contour, key=cv2.contourArea,
                        reverse=True)  # сортируем серию координат точек контура по площади, которую они окружают
        ret_np = np.ones(dst.shape, np.uint8)  # создаем черный занавес
        for i in range(len(contour)):
            continious_hand_bw_mask = cv2.drawContours(ret_np, [contour[i]], -1, (255, 255, 255), thickness=-1)
        continious_hand_bw_mask = np.where((continious_hand_bw_mask == 1), 0, 255).astype('uint8')

        cv2.imwrite(folder_name_path + '/{}_hand_on_black_back.jpg'.format(image_name), skin_color)
        cv2.imwrite(folder_name_path + '/{}_continious_hand_bw_mask.jpg'.format(image_name), continious_hand_bw_mask)


    def getting_mask(self, config_dict, filename, roi, points):
        image_name = filename[:-4]
        processed_path = config_dict['preprocessing']['processed_folder'] 
        folder_name_path = processed_path + image_name + '/'
        empty_table_path = "empty_table.jpg"
        YCrCb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCR_CB)  # преобразуем в пространство YCrCb
        (y, cr, cb) = cv2.split(YCrCb)  # выделяем значения Y, Cr, Cb
        cr1 = cv2.GaussianBlur(cr, (5, 5), 0)  # фильтр Гаусса для небольшого размытия
        _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # ostuprocessing
        res = cv2.bitwise_and(roi, roi, mask=skin)
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        dst = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
        Laplacian = cv2.convertScaleAbs(dst)
        h = cv2.findContours(Laplacian, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # находим на изображении контуры
        contour = h[0]
        contour = sorted(contour, key=cv2.contourArea,
                        reverse=True)  # сортируем серию координат точек контура по площади, которую они окружают
        ret_np = np.ones(dst.shape, np.uint8)  # создаем черный занавес
        for i in range(len(contour)):
            continious_hand_bw_mask = cv2.drawContours(ret_np, [contour[i]], -1, (255, 255, 255), thickness=-1)
        empty_table = cv2.imread(empty_table_path)  # считываем фото пустого стола
        empty_table_roi = empty_table[points[2]:points[3], points[0]:points[1]]  # выделяем область интереса ROI
        continious_hand_bw_mask = np.where((continious_hand_bw_mask == 1), 0, 255).astype('uint8')
        mask_inv = cv2.bitwise_not(continious_hand_bw_mask)
        empty_table_fg = cv2.bitwise_and(empty_table_roi, empty_table_roi, mask=continious_hand_bw_mask)
        hand_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        dst = cv2.add(empty_table_fg, hand_bg)  # not bad
        dst_copy = dst.copy()
        dst_copy = cv2.cvtColor(dst_copy, cv2.COLOR_BGR2GRAY)
        im = PIL.Image.fromarray(np.uint8(dst_copy))
        mean = ImageStat.Stat(im).mean
        _, bw_mask_thresh = cv2.threshold(dst_copy, mean[0], 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
        bw_mask = cv2.bitwise_and(dst_copy, dst_copy, mask=bw_mask_thresh)

        cv2.imwrite(folder_name_path + '/{}_detail_bw_mask.jpg'.format(image_name), np.array(bw_mask_thresh))
        cv2.imwrite(folder_name_path + '/{}_detail_on_black_bg.jpg'.format(image_name), np.array(bw_mask))


    def check_and_create_directories(self, config_dict):
        if not os.path.exists(config_dict['preprocessing']['processed_folder']):
            os.makedirs(config_dict['preprocessing']['processed_folder'])


    def nn_labeling(self, config_dict, increment_hsStatus):
        photo_num = 0
        self.labels = sorted(os.listdir(config_dict['1_step']['raw_photos_path']))
        for i in range(len(self.labels)):
            my_path = config_dict['1_step']['raw_photos_path'] + self.labels[i] + "/"
            try:
                photo_num += len(os.listdir(my_path))
            except:
                pass
        increment = 1 / photo_num
        for i in range(len(self.labels)):
            my_path = config_dict['1_step']['raw_photos_path'] + self.labels[i] + "/"
            for filename_batch in self.batch(os.listdir(my_path), os.cpu_count() - active_count()):
                thread_batch = list()
                for filename in filename_batch:
                    if filename[filename.rfind(".") + 1:] in ['jpg', 'png']:
                        raw_detail_path = my_path + filename   # !!!
                        thread_batch.append(Thread(
                                                target=self.preprocessing_with_nn,
                                                args=(config_dict, raw_detail_path, filename, 
                                                config_dict['preprocessing']['processed_folder']),
                                                kwargs={'eps': 100, 'show': False, 'save': True,
                                                'need_hand': config_dict['preprocessing']['hand_indicator'],
                                                'increment_hsStatus': increment_hsStatus,
                                                'increment': increment})
                                            )
                for thread in thread_batch:
                    thread.start()
                for thread in thread_batch:
                    thread.join()
                thread_batch.clear()


    def main_job(self, signal: Signal, increment_hsStatus: Function, config_dict) -> None:
        '''Starts the main job of the class

        Creates a thread for each image in the directory and starts mediapipe
        
        Args:
            signal (Signal): Signal to emit when the job is done
            increment_hsStatus (function): Function to increment the status of the job
        '''
        # DIRS
        self.check_and_create_directories(config_dict)
        config_dict['name_list'] = os.listdir(config_dict['1_step']['raw_photos_path'])

        # ROI-getting:
        self.nn_labeling(config_dict, increment_hsStatus)
            
        signal.emit()

if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    hs = HandSegmentor(config)
    hs.main_job()

