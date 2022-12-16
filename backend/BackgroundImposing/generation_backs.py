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
        # self.all_details_names = os.listdir(config['filepath'])
        self.all_details_names = config['name_list']
        # if 'Blank_surfaces' in self.all_details_names:
        #     self.all_details_names.remove('Blank_surfaces')
        # if 'Blank_surface' in self.all_details_names:
        #     self.all_details_names.remove('Blank_surface')
        # if 'processed' in self.all_details_names:
        #     self.all_details_names.remove('processed')
        # if '.gitignore' in self.all_details_names:
        #     self.all_details_names.remove('.gitignore')
        # if 'backgrounds' in self.all_details_names:
        #     self.all_details_names.remove('backgrounds')
        # if 'hand' not in self.all_details_names:
        #     self.all_details_names.append('hand')
        # if 'generated_images' in self.all_details_names:
        #     self.all_details_names.remove('generated_images')
        # if not os.path.exists(config['generated_images']):
        #     os.mkdir(config['generated_images'])
        self.backgrounds = config['generation_backs']['backgrounds']
        self.generated_images = config['generation_backs']['generation_folder']
        self.height = config['generation_backs']['height']
        self.width = config['generation_backs']['width']
        self.final_height = config['generation_backs']['final_height']
        self.final_width = config['generation_backs']['final_width']
        self.iou = config['generation_backs']['iou']

        # self.max_number_of_details = config['max_number_of_details']


    def get_score(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        iou = interArea / float(boxAArea + boxBArea - interArea)
        # xA = max(boxA[1], boxB[1])
        # yA = max(boxA[0], boxB[0])
        # xB = min(boxA[3], boxB[3])
        # yB = min(boxA[2], boxB[2])

        # # xA = max(boxA[0], boxB[0])
        # # yA = max(boxA[1], boxB[1])
        # # xB = min(boxA[2], boxB[2])
        # # yB = min(boxA[3], boxB[3])
        # interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        # boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        # boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        # iou = interArea / float(boxAArea + boxBArea - interArea)
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
           for i in range(int(rect[0]), int(rect[2])): #rect, background are y, x. So i = y, j = x
                for j in range(int(rect[1]), int(rect[3])):
                    if mask_gray[i - sdvig_y][j - sdvig_x] > 250:
                        background[i][j] = img[i - sdvig_y][j - sdvig_x]
                        prev_mask[i][j] = mask_gray[i - sdvig_y][j - sdvig_x]
        else:
            for i in range(img.shape[0]):   # (int(rect[1]), int(rect[3])):
                for j in range(img.shape[1]):  # (int(rect[0]), int(rect[2])):
                    # if mask_gray[i - sdvig_y][j - sdvig_x] > 250:
                    # background[i + sdvig_y][j + sdvig_x] = img[i][j]  # img[i - sdvig_y][j - sdvig_x]
                    background[i + sdvig_y][j + sdvig_x] = img[i][j]  # img[i - sdvig_y][j - sdvig_x]
                    prev_mask[i + sdvig_y][j + sdvig_x] = 255 # mask_gray[i - sdvig_y][j - sdvig_x]
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
        #sdvig_y = int(random.uniform(0, background.shape[1] - mask_gray.shape[1]))
        #sdvig_x = int(random.uniform(0, background.shape[0] - mask_gray.shape[0]))
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
        # detail = cv2.imread(path_detail) # SHAPE - y, x
        # mask = cv2.imread(path_mask) 
        # print("path_mask = ", path_mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY) # SHAPE - y, x
        rot = 0 # !!!!!! пока что

        if detail_name == "hand":
            detail, mask = apply_augmentations(detail, mask, vert_flip, horiz_flip, rot=rot)
            
            approx = self.get_approx(mask, detail_name)
            if approx is np.nan:
                print("Approx is empty")
                return img, masks_array, d, detail_num, square
            yolo_points = self.get_yolo_points(approx)
        else:
            yolo_points = [0, 0, mask.shape[0], mask.shape[1]]  # self.get_yolo_points(approx) # SHAPE - y, x
        
        sdvig_x, sdvig_y = self.get_shifts(img, mask)
        rect = [yolo_points[0] + sdvig_y, yolo_points[1] + sdvig_x, yolo_points[2] + sdvig_y, yolo_points[3] + sdvig_x] # SHAPE - y, x
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

# 1) pass config_dict, not parameters +
# 2) if roi then else masks -> another idea


# 3) In roi add shuffle, and rotation (on number_iterations / number_of_masks * 90). In all 4 * number_of_masks iterations
# 4) Make generation with rotation for roi

# 5) Make mask generation like it was

    def check_and_create_directories(self, config_dict):
        if not os.path.exists(config_dict['generation_backs']['generation_folder']):
            os.makedirs(config_dict['generation_backs']['generation_folder'])

    def main_job(self, config_dict): # -> Generator[float, None, None]:
        '''Starts the main job of the class
        
        Args:
            photo_num (int): number of photos to generate
        
        Yields:
            float: percentage of the job done
        '''
        print("YOUR CONF IS", config_dict)
        self.check_and_create_directories(config_dict)
        backgrounds = config_dict['generation_backs']['backgrounds']
        print("YOUR BACK IS", backgrounds)
        self.iou = config_dict['generation_backs']['iou']
        photo_num = int(config_dict['generation_backs']['photo_num'])
        generation_folder = config_dict['generation_backs']['generation_folder']
        processed_path = config_dict['preprocessing']['processed_folder']
        max_details_on_photo = config_dict['generation_backs']['max_details_on_photo']
        max_hands_on_photo = config_dict['generation_backs']['max_hands_on_photo']

        lst = os.listdir(processed_path)
        all_details_names = list(set(lst[i][:lst[i].rfind('_')] for i in range(len(lst))))
        if int(config_dict['generation_backs']['max_hands_on_photo']) > 0:
            all_details_names.append("hand")
        config_dict['name_list'] = all_details_names
        self.all_details_names = all_details_names
        self.define_dict_for_yolo(config_dict)
        print("all_details_names", all_details_names)
        number_of_used_masks = config_dict['generation_backs']['number_of_masks']
        print("number_of_used_masks", number_of_used_masks)
        number_of_hand_masks = config_dict['generation_backs']['number_of_hand_masks']
        if config_dict['generation_backs']['rectangle_indicator'] != 1:
            number_of_used_masks = photo_num * max_details_on_photo
        
        all_mask_folders = config_dict['generation_backs']['all_mask_folders']  #os.listdir(processed_path)
        all_hand_folders = config_dict['generation_backs']['all_hand_folders']

        print("LEN", len(all_mask_folders), len(all_hand_folders))

        masks_index_list = np.arange(len(all_mask_folders))
        hand_index_list = np.arange(len(all_hand_folders))

        random.shuffle(masks_index_list)
        position = 0
        hand_position = 0

        print("iou is", self.iou)
        print("PHOTO_NUM IS", photo_num)
        print("\n\ncount_masks", number_of_hand_masks, "\nlst of masks", all_hand_folders, "\n\n")
        print("\n\ncount_masks", config_dict['generation_backs']['number_of_masks'], "\nlst of masks", config_dict['generation_backs']['all_mask_folders'], "\n\n")
        max_square = self.height * self.width
        
        for id in range(photo_num):
            print("PHOTO_NUM IS", photo_num)
            print("iou IS", self.iou)
            square = 0  # square of overlayed details
            name_back = backgrounds + '/' + random.choice(os.listdir(backgrounds))
            background = resize_specific_width_and_height(cv2.imread(name_back), self.width, self.height)
            img = background
            masks_array = np.zeros((self.height * self.width * 20)).reshape((self.height, self.width, 20))
            number_of_details_on_photo = int(random.uniform(1, max_details_on_photo))
            print(f'amount of details is {number_of_details_on_photo} for img_{id}')
            detail_num = 0
            current_number_of_hands_on_photo = 0
            while detail_num < number_of_details_on_photo and square < max_square:
                if detail_num == 0:
                    d = {}
                j = int(random.uniform(0, len(all_details_names)))  # номер детали из комплекта
                detail_name = all_details_names[j]
                if detail_name == "hand" and current_number_of_hands_on_photo < max_hands_on_photo:
                    # print("hand_index_list", hand_index_list)
                    # print("hand_position", hand_position)
                    detail_path, mask_path = get_hand_path(hand_index_list[hand_position], all_hand_folders, processed_path)
                    hand_position += 1
                    detail_image = cv2.imread(detail_path) 
                    mask_image = cv2.imread(mask_path)
                    detail_image = scale_image_in_percent(detail_image, 3)
                    mask_image = scale_image_in_percent(mask_image, 3)
                    current_number_of_hands_on_photo += 1
                else:
                    # detail_path, mask_path = get_detail_path(detail_name, processed_path)
                    detail_path, detail_name = get_shuffle_detail_path(masks_index_list[position], all_mask_folders, processed_path)
                    # print("\ndetail_path:", detail_path, "\n\n")
                    # mask_path = detail_path
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
                # print("D IS", d, "\ndet_num =", detail_num, "\nnumber_of_details_on_photo", number_of_details_on_photo)
                # print(f'square {square} max_square {max_square}')
            number_of_details_on_photo = detail_num
            file_name = f'image_{id}'
            self.write_yolo_txt(d, file_name, number_of_details_on_photo)
            #img = resize_specific_width_and_height(img, self.final_width, self.final_height)
            cv2.imwrite(f'{generation_folder}/{file_name}.jpg', img)
            yield (id + 1) / photo_num


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    bg = BacksGeneration(config)
    bg.main_job()
