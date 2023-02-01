from typing import Generator
import numpy as np
import cv2
import time
import json
import os
import random
from backend.BackgroundImposing.dict4json import Dict4Json
from backend.BackgroundImposing.augmentations import *
from backend.BackgroundImposing.paths import *

class BacksGeneration(Dict4Json):

    def __init__(self, config):
        super().__init__(config)
        self.processed_folder = config['preprocessing']['processed_folder'][0]
        self.all_details_names = config['name_list']
        self.backgrounds = config['generation_backs']['backgrounds']
        self.generated_images = config['generation_backs']['generation_folder']
        self.height = config['generation_backs']['height']
        self.width = config['generation_backs']['width']
        self.final_height = config['generation_backs']['final_height']
        self.final_width = config['generation_backs']['final_width']
        self.iou = config['generation_backs']['iou']


    def get_score(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou


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


    def generate_new_background(self, detail_num, detail_name, img, mask_gray, background, sdvig_x, sdvig_y, rect):
        """
        Функция-посредник: при необходимости меняет размерность фона
        и добавляет новые элементы на фон.
        :param detail_num: int
        :param img: array
        :param mask_gray: array
        :param background: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, int
        """
        if (detail_num < 1):
            background = resize_specific_width_and_height(background, self.width, self.height)
        if self.rectangle_indicator:
            background, gt = self.add_object_on_background_by_rect(img, mask_gray, background, sdvig_x, sdvig_y)
        else:
            background, gt = self.add_object_on_background_by_segm(img, mask_gray, background, sdvig_x, sdvig_y, rect)
        return background, gt


    def add_object_on_background_by_segm(self, img, mask_gray, background, sdvig_x, sdvig_y, rect):
        """
        Функция отрисовки новой детали на фоне.
        :param img: array
        :param mask_gray: array
        :param background: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, array
        """         
        prev_mask = np.zeros((self.height, self.width))
        for i in range(int(rect[1]), int(rect[3])):
            for j in range(int(rect[0]), int(rect[2])):
                if mask_gray[i - sdvig_y][j - sdvig_x] > 250:
                    background[i][j] = img[i - sdvig_y][j - sdvig_x]
                    prev_mask[i][j] = mask_gray[i - sdvig_y][j - sdvig_x]
        return background, prev_mask


    def add_object_on_background_by_rect(self, img, mask_gray, background, sdvig_x, sdvig_y):
        """
        Функция отрисовки новой детали на фоне.
        :param img: array
        :param mask_gray: array
        :param background: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, array
        """ 
        cur_mask = self.get_mask(mask_gray, sdvig_x, sdvig_y)
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                background[i + sdvig_y][j + sdvig_x] = img[i][j] 
        return background, cur_mask

    def get_mask(self, mask_gray, sdvig_x, sdvig_y):
        """
        Функция получения маски детали в формате full-hd.
        :param mask_gray: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array
        """
        cur_mask = np.zeros((self.height, self.width))
        for i in range(mask_gray.shape[0]):
            for j in range(mask_gray.shape[1]):
                if mask_gray[i][j] > 250:
                    cur_mask[i + sdvig_y][j + sdvig_x] = 255
        return cur_mask


    def get_shifts(self, background, mask_gray):
        """
        Генерация сдвигов по осям х/у.
        :param background: array
        :param mask_gray: array
        :return: int, int
        """
        sdvig_y = int(random.uniform(0, background.shape[0] - mask_gray.shape[0]))
        sdvig_x = int(random.uniform(0, background.shape[1] - mask_gray.shape[1]))
        return sdvig_x, sdvig_y


    def check_iou(self, d, rect1, detail_num):
        """
        Проверка IoU.
        :param d: dictionary
        :param rect1: array
        :param detail_num: int
        :return: int (0 or 1)
        """
        flag = 1
        for i in range(detail_num):
            score = self.get_score(d["annotations"][i]["yolo"], rect1)
            if score > self.iou:
                flag = 0
                break
            score = self.get_score(rect1, d["annotations"][i]["yolo"])
            if score > self.iou:
                flag = 0
                break
        return flag


    def generate_new_photo(self, detail_num, id, detail_name, img, detail, mask, background, masks_array,
                            count, d, square, config_dict):
        """
        Генерация нового изображения
        :param detail_num: int - номер (порядок) детали среди всех, нанесенных на изображение с этим id
        :param id: int - id изображения, unique
        :param detail_name: str - имя детали
        :param img: array
        :param path_detail: str
        :param path_mask: str
        :param background: array
        :param masks_array: array
        :param count: int - количество деталей на изображении
        :param d: dictionary
        :param vert_flip: int (0 or 1)
        :param horiz_flip: int (0 or 1)
        :param rot: int
        :return: array, array, dictionary, int
        """
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        if self.rectangle_indicator:
            yolo_points = [0, 0, mask.shape[0], mask.shape[1]]  
            sdvig_x, sdvig_y = self.get_shifts(img, mask)
            rect = [yolo_points[0] + sdvig_y, yolo_points[1] + sdvig_x, yolo_points[2] + sdvig_y, yolo_points[3] + sdvig_x]
            rect_for_iou = [yolo_points[1] + sdvig_x, yolo_points[0] + sdvig_y, yolo_points[3] + sdvig_x, yolo_points[2] + sdvig_y] 
        else:
            approx = self.get_approx(mask, detail_name)
            if approx is np.nan:
                print("Approx is empty")
                return img, masks_array, d, detail_num, square
            yolo_points = self.get_yolo_points(approx, self.rectangle_indicator)
            sdvig_x, sdvig_y = self.get_shifts(img, mask)
            rect = [yolo_points[0] + sdvig_x, yolo_points[1] + sdvig_y, yolo_points[2] + sdvig_x, yolo_points[3] + sdvig_y]
            rect_for_iou = rect

        square += (yolo_points[2] - yolo_points[0]) * (yolo_points[3] - yolo_points[1])

        if detail_num == 0:
            d = self.writing_in_json(detail_num, img, detail_name, id, rect, count, d, self.all_details_names, config_dict)
            img, masks_array[:, :, 0] = self.generate_new_background(detail_num, detail_name, detail, mask, background, sdvig_x, sdvig_y, rect)
        else:
            flag = self.check_iou(d, rect_for_iou, detail_num)
            if flag == 1:
                d = self.writing_in_json(detail_num, img, detail_name, id, rect, count, d, self.all_details_names, config_dict)
                if self.rectangle_indicator:
                    img, masks_array[:, :, detail_num] = self.add_object_on_background_by_rect(detail, mask, img, sdvig_x, sdvig_y)
                else:
                    img, masks_array[:, :, detail_num] = self.add_object_on_background_by_segm(detail, mask, img, sdvig_x, sdvig_y, rect)
            else:
                return img, masks_array, d, detail_num, square
        return img, masks_array, d, detail_num + 1, square


    def apply_augmentations(self, detail, mask, vert_flip=True, horiz_flip=True, rot=True, scale=True):
        if vert_flip:
            vf = int(random.uniform(0, 2))
            detail = vertical_flip(detail, vf)
            mask = vertical_flip(mask, vf)
        if horiz_flip:
            hf = int(random.uniform(0, 2))
            detail = horizontal_flip(detail, hf)
            mask = horizontal_flip(mask, hf)
        if rotation:
            if self.rectangle_indicator:
                angle = int(random.uniform(0, 4)) * 90
                detail = rotation90(detail, angle)
                mask = rotation90(mask, angle)
            else:
                angle = int(random.uniform(0, 360))
                detail = rotation(detail, angle)
                mask = rotation(mask, angle)
        if scale:
            proportion = float(random.uniform(self.min_scaling, self.max_scaling))
            print(f'proportion {proportion}')
            detail = scale_image_in_percent(detail, proportion)
            mask = scale_image_in_percent(mask, proportion)

        return detail, mask
        
    def check_and_create_directories(self, config_dict):
        if not os.path.exists(config_dict['generation_backs']['generation_folder']):
            os.makedirs(config_dict['generation_backs']['generation_folder'])
        if not os.path.exists(config_dict['generation_backs']['yolo_folder']):
            os.makedirs(config_dict['generation_backs']['yolo_folder'])

    
    def define_names(self, config_dict):
        self.processed_folder = config_dict['generation_backs']['processed_folders'][0]  + '/'

        self.backgrounds = config_dict['generation_backs']['backgrounds'] + '/'
        self.iou = config_dict['generation_backs']['iou']
        self.photo_num = int(config_dict['generation_backs']['photo_num'])
        self.generation_folder = config_dict['generation_backs']['generation_folder'] + '/'
        self.yolo_folder = config_dict["generation_backs"]["yolo_folder"] + '/'
        self.max_details_on_photo = config_dict['generation_backs']['max_details_on_photo']
        self.min_scaling = config_dict['generation_backs']['min_scaling']
        self.max_scaling = config_dict['generation_backs']['max_scaling']
        self.max_square = self.height * self.width
        self.rectangle_indicator = config_dict['generation_backs']['rectangle_indicator']

        lst = sorted(os.listdir(self.processed_folder))  # add general lst for all folders, not only one
        self.all_details_names = sorted(list(set(lst[i][:lst[i].rfind('_')] for i in range(len(lst)))))
        config_dict['name_list'] = self.all_details_names
        # config_dict['name_list'] = os.listdir(self.raw_photos_path)
        self.define_dict_for_yolo(config_dict)
        self.number_of_used_masks = config_dict['generation_backs']['number_of_masks']
        if config_dict['generation_backs']['rectangle_indicator'] != 1:
            self.number_of_used_masks = self.photo_num * self.max_details_on_photo

        self.processed_folders = []
        self.folder_weights = []
        for folder in config_dict['generation_backs']['processed_folders']:
            self.processed_folders.append(folder + '/')
            self.folder_weights.append(len(os.listdir(folder + '/')))


        

    def main_job(self, config_dict): # -> Generator[float, None, None]:
        '''Starts the main job of the class
        
        Args:
            photo_num (int): number of photos to generate
        
        Yields:
            float: percentage of the job done
        '''
        self.check_and_create_directories(config_dict)
        self.define_names(config_dict)
        id = 0
        while id < self.photo_num:
            square = 0  # square of overlayed details
            name_back = self.backgrounds + random.choice(os.listdir(self.backgrounds))
            background = cv2.imread(name_back)
            background = resize_specific_width_and_height(background, self.width, self.height)
            img = background
            masks_array = np.zeros((self.height * self.width * 20)).reshape((self.height, self.width, 20))
            number_of_details_on_photo = int(random.uniform(1, self.max_details_on_photo) + 1)
            detail_num = 0
            while detail_num < number_of_details_on_photo and square < self.max_square:
                id_folder = random.choices(range(len(self.processed_folders)), weights=self.folder_weights)[0]
                self.processed_folder = self.processed_folders[id_folder]
                print(f'self.processed_path {self.processed_folder}')
                if detail_num == 0:
                    d = {}
                j = int(random.uniform(0, len(self.all_details_names)))  # номер детали из комплекта
                # if detail does no consist in processed folder, then pass this detail
                detail_name = self.all_details_names[j]
                if self.rectangle_indicator:
                    detail_path = get_detail_path_by_rect(detail_name, self.processed_folder)
                    if detail_path == '':
                        continue
                    else:
                        print(f'detail_path {detail_path}')
                        detail_image, mask_image = cv2.imread(detail_path), cv2.imread(detail_path)

                else:
                    detail_path, mask_path = get_detail_path_by_segm(detail_name, self.processed_folder)
                    detail_image, mask_image = cv2.imread(detail_path), cv2.imread(mask_path)

                detail_image, mask_image = self.apply_augmentations(detail_image, mask_image)
                img, masks_array, d, detail_num, square = self.generate_new_photo(detail_num, id, detail_name, img, detail_image, mask_image,
                                                    background, masks_array, count=number_of_details_on_photo, d=d, square=square,
                                                    config_dict=config_dict)
            number_of_details_on_photo = detail_num
            file_name = f'image_{id}'
            self.write_yolo_txt(d, file_name, number_of_details_on_photo, self.yolo_folder)
            img = resize_specific_width_and_height(img, self.final_width, self.final_height)
            cv2.imwrite(f'{self.generation_folder}/{file_name}.jpg', img)
            id += 1
            yield id / self.photo_num


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    bg = BacksGeneration(config)
    bg.main_job()
