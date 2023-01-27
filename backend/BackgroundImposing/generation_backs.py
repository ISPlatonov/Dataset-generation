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
        self.processed_path = config['preprocessing']['processed_folder']
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
        area = black_and_white_mask.shape[0] * black_and_white_mask.shape[1]
        if cv2.contourArea(approx) / area > 0.23 and detail_name != "hand":
            print(f'The area of contours is {cv2.contourArea(approx) / area}')
            return np.nan
        return approx


    def generate_new_background(self, detail_num, detail_name, img, mask_gray, background1, sdvig_x, sdvig_y, rect):
        """
        Функция-посредник: при необходимости меняет размерность фона
        и добавляет новые элементы на фон.
        :param detail_num: int
        :param img: array
        :param mask_gray: array
        :param background1: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, int
        """
        if (detail_num < 1):
            background1 = resize_specific_width_and_height(background1, self.width, self.height)
        background1, gt = self.adding_img_on_background(img, mask_gray, detail_name, background1, sdvig_x, sdvig_y, rect)
        return background1, gt



    def adding_img_on_background(self, img, mask_gray, detail_name, background, sdvig_x, sdvig_y, rect):
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
        if detail_name == "hand":
           for i in range(int(rect[0]), int(rect[2])):
                for j in range(int(rect[1]), int(rect[3])):
                    if mask_gray[i - sdvig_y][j - sdvig_x] > 250:
                        background[i][j] = img[i - sdvig_y][j - sdvig_x]
                        prev_mask[i][j] = mask_gray[i - sdvig_y][j - sdvig_x]
        else:
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    background[i + sdvig_y][j + sdvig_x] = img[i][j] 
                    prev_mask[i + sdvig_y][j + sdvig_x] = 255
        return background, prev_mask

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


    def add_detail_on_background(self, img, mask_gray, detail_name, background, sdvig_x, sdvig_y, rect):
        """
        Добавление детали на фон.
        :param img: array
        :param mask_gray: array
        :param background: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, array
        """
        cur_mask = self.get_mask(mask_gray, sdvig_x, sdvig_y)
        background, _ = self.adding_img_on_background(img, mask_gray, detail_name, background, sdvig_x, sdvig_y, rect)
        return background, cur_mask


    def generate_new_photo(self, detail_num, id, detail_name, img, detail, mask, background, masks_array,
                            count, d, square, config_dict, vert_flip=0, horiz_flip=0, rot=0):
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
        rot = 0

        if detail_name == "hand":
            detail, mask = apply_augmentations(detail, mask, vert_flip, horiz_flip, rot=rot)
            
            approx = self.get_approx(mask, detail_name)
            if approx is np.nan:
                print("Approx is empty")
                return img, masks_array, d, detail_num, square
            yolo_points = self.get_yolo_points(approx)
        else:
            yolo_points = [0, 0, mask.shape[0], mask.shape[1]]  
        
        sdvig_x, sdvig_y = self.get_shifts(img, mask)
        rect = [yolo_points[0] + sdvig_y, yolo_points[1] + sdvig_x, yolo_points[2] + sdvig_y, yolo_points[3] + sdvig_x]
        rect_for_iou = [yolo_points[1] + sdvig_x, yolo_points[0] + sdvig_y, yolo_points[3] + sdvig_x, yolo_points[2] + sdvig_y] 
        square += (yolo_points[2] - yolo_points[0]) * (yolo_points[3] - yolo_points[1])
        if detail_num == 0:
            d = self.writing_in_json(detail_num, img, detail_name, id, rect, count, d, self.all_details_names, config_dict)
            img, masks_array[:, :, 0] = self.generate_new_background(detail_num, detail_name, detail, mask, background, sdvig_x, sdvig_y, rect)
        else:
            flag = self.check_iou(d, rect_for_iou, detail_num)
            if flag == 1:
                d = self.writing_in_json(detail_num, img, detail_name, id, rect, count, d, self.all_details_names, config_dict)
                img, masks_array[:, :, detail_num] = self.add_detail_on_background(detail, mask, detail_name, img, sdvig_x, sdvig_y, rect)
            else:
                return img, masks_array, d, detail_num, square
        return img, masks_array, d, detail_num + 1, square


    def check_and_create_directories(self, config_dict):
        if not os.path.exists(config_dict['generation_backs']['generation_folder']):
            os.makedirs(config_dict['generation_backs']['generation_folder'])
        if not os.path.exists(config_dict['generation_backs']['yolo_folder']):
            os.makedirs(config_dict['generation_backs']['yolo_folder'])


    def main_job(self, config_dict): # -> Generator[float, None, None]:
        '''Starts the main job of the class
        
        Args:
            photo_num (int): number of photos to generate
        
        Yields:
            float: percentage of the job done
        '''
        self.check_and_create_directories(config_dict)
        backgrounds = config_dict['generation_backs']['backgrounds']
        self.iou = config_dict['generation_backs']['iou']
        photo_num = int(config_dict['generation_backs']['photo_num'])
        generation_folder = config_dict['generation_backs']['generation_folder']
        processed_path = config_dict['preprocessing']['processed_folder']
        max_details_on_photo = config_dict['generation_backs']['max_details_on_photo']
        max_hands_on_photo = config_dict['generation_backs']['max_hands_on_photo']

        lst = sorted(os.listdir(processed_path))
        all_details_names = sorted(list(set(lst[i][:lst[i].rfind('_')] for i in range(len(lst)))))
        config_dict['name_list'] = all_details_names
        self.all_details_names = all_details_names
        self.define_dict_for_yolo(config_dict)
        print(f'\n\nnames: {config_dict["name_list"]}\n\n')
        number_of_used_masks = config_dict['generation_backs']['number_of_masks']
        number_of_hand_masks = config_dict['generation_backs']['number_of_hand_masks']
        if config_dict['generation_backs']['rectangle_indicator'] != 1:
            number_of_used_masks = photo_num * max_details_on_photo
        
        all_mask_folders = config_dict['generation_backs']['all_mask_folders'] 
        all_hand_folders = config_dict['generation_backs']['all_hand_folders']

        masks_index_list = np.arange(len(all_mask_folders))
        hand_index_list = np.arange(len(all_hand_folders))

        random.shuffle(masks_index_list)
        position = 0
        hand_position = 0

        max_square = self.height * self.width
        id = 0
        
        # for id in range(number_of_used_masks):
        while position < number_of_used_masks:

            square = 0  # square of overlayed details
            name_back = backgrounds + '/' + random.choice(os.listdir(backgrounds))
            background = resize_specific_width_and_height(cv2.imread(name_back), self.width, self.height)
            img = background
            masks_array = np.zeros((self.height * self.width * 20)).reshape((self.height, self.width, 20))
            number_of_details_on_photo = int(random.uniform(1, max_details_on_photo))
            detail_num = 0
            current_number_of_hands_on_photo = 0
            while detail_num < number_of_details_on_photo and square < max_square:
                if detail_num == 0:
                    d = {}
                j = int(random.uniform(0, len(all_details_names)))  # номер детали из комплекта
                detail_name = all_details_names[j]
                if detail_name == "hand" and current_number_of_hands_on_photo < max_hands_on_photo:
                    detail_path, mask_path = get_hand_path(hand_index_list[hand_position], all_hand_folders, processed_path)
                    hand_position += 1
                    detail_image = cv2.imread(detail_path) 
                    mask_image = cv2.imread(mask_path)
                    detail_image = scale_image_in_percent(detail_image, 3)
                    mask_image = scale_image_in_percent(mask_image, 3)
                    current_number_of_hands_on_photo += 1
                else:
                    detail_path, detail_name = get_shuffle_detail_path(masks_index_list[position], all_mask_folders, processed_path)
                    detail_image, mask_image = cv2.imread(detail_path), cv2.imread(detail_path)
                    detail_image = scale_image_in_percent(detail_image, 3)
                    mask_image = scale_image_in_percent(mask_image, 3)
                    detail_image = rotation(detail_image, (masks_index_list[position] % 4) * 90)
                    mask_image = rotation(mask_image, (masks_index_list[position] % 4) * 90)
                    position += 1
                    if position == number_of_used_masks:
                        number_of_details_on_photo = detail_num
                        id = photo_num
                        break
                vf = int(random.uniform(0, 2))
                hf = int(random.uniform(0, 2))
                vf = int(random.uniform(0, 2))
                rot = int(random.uniform(0, 360))
                img, masks_array, d, detail_num, square = self.generate_new_photo(detail_num, id, detail_name, img, detail_image, mask_image,
                                                    background, masks_array, count=number_of_details_on_photo, d=d, square=square, vert_flip=vf, horiz_flip=hf, rot=rot,
                                                    config_dict=config_dict)
            number_of_details_on_photo = detail_num
            file_name = f'image_{id}'
            self.write_yolo_txt(d, file_name, number_of_details_on_photo, config_dict["generation_backs"]["yolo_folder"])
            img = resize_specific_width_and_height(img, self.final_width, self.final_height)
            cv2.imwrite(f'{generation_folder}/{file_name}.jpg', img)
            id += 1
            yield (position + 1) / number_of_used_masks


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    bg = BacksGeneration(config)
    bg.main_job()
