import numpy as np
import cv2
import time
import json
from backend.BackgroundImposing.dict4json import *
from backend.BackgroundImposing.augmentations import *
from backend.BackgroundImposing.paths import *


class BacksGeneration:

    def __init__(self, config):
        self.processed_path = config['processed_path']
        self.all_details_names = os.listdir(config['filepath'])
        if 'Blank_surface' in self.all_details_names:
            self.all_details_names.remove('Blank_surface')
        if 'processed' in self.all_details_names:
            self.all_details_names.remove('processed')
        if '.gitignore' in self.all_details_names:
            self.all_details_names.remove('.gitignore')
        if 'backgrounds' in self.all_details_names:
            self.all_details_names.remove('backgrounds')
        self.backgrounds = config['backgrounds']
        self.generated_images = config['generated_images']


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
        if (len(cnts) > 3 or len(cnts) == 0) and detail_name != "hand":
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
            return np.nan
        return approx


    def generate_new_background(self, detail_num, img, mask_gray, background1, sdvig_x, sdvig_y):
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
            background1 = resize_specific_width_and_height(background1, 1920, 1080)
        background1, gt = self.adding_img_on_background(img, mask_gray, background1, sdvig_x, sdvig_y)
        return background1, gt


    def adding_img_on_background(self, img, mask_gray, background, sdvig_x, sdvig_y):
        """
        Функция отрисовки новой детали на фоне.
        :param img: array
        :param mask_gray: array
        :param background: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array, array
        """
        prev_mask = np.zeros((1080, 1920))
        for i in range(mask_gray.shape[0]):
            for j in range(mask_gray.shape[1]):
                if mask_gray[i][j] > 250:
                    background[i + sdvig_y][j + sdvig_x][0] = img[i][j][0]
                    background[i + sdvig_y][j + sdvig_x][1] = img[i][j][1]
                    background[i + sdvig_y][j + sdvig_x][2] = img[i][j][2]
                    prev_mask[i + sdvig_y][j + sdvig_x] = mask_gray[i][j]
        return background, prev_mask


    def get_mask(self, mask_gray, sdvig_x, sdvig_y):
        """
        Функция получения маски детали в формате full-hd.
        :param mask_gray: array
        :param sdvig_x: int
        :param sdvig_y: int
        :return: array
        """
        cur_mask = np.zeros((1080, 1920))
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
            if score > 0.2:
                flag = 0
                break
            score = self.get_score(rect1, d["annotations"][i]["yolo"])
            if score > 0.2:
                flag = 0
                break
        return flag


    def add_detail_on_background(self, img, mask_gray, background, sdvig_x, sdvig_y):
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
        background, _ = self.adding_img_on_background(img, mask_gray, background, sdvig_x, sdvig_y)
        return background, cur_mask


    def generate_new_photo(self, detail_num, id, detail_name, img, path_detail, path_mask, background, masks_array,
                            count, d, vert_flip=0, horiz_flip=0, rot=0):
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
        detail = cv2.imread(path_detail)
        mask = cv2.imread(path_mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        detail, mask = apply_augmentations(detail, mask, vert_flip, horiz_flip, rot=rot)
        approx = self.get_approx(mask, detail_name)
        if approx is np.nan:
            print("Approx is empty")
            return img, masks_array, d, detail_num
        yolo_points = get_yolo_points(approx)
        sdvig_x, sdvig_y = self.get_shifts(img, mask)
        rect = [yolo_points[0] + sdvig_x, yolo_points[1] + sdvig_y, yolo_points[2] + sdvig_x, yolo_points[3] + sdvig_y]
        if detail_num <= 0:
            d = writing_in_json(detail_num, img, detail_name, id, rect, count, d)
            img, masks_array[:, :, 0] = self.generate_new_background(detail_num, detail, mask, background, sdvig_x, sdvig_y)
        else:
            flag = self.check_iou(d, rect, detail_num)
            if flag == 1:
                d = writing_in_json(detail_num, img, detail_name, id, rect, count, d)
                img, masks_array[:, :, detail_num] = self.add_detail_on_background(detail, mask, img, sdvig_x, sdvig_y)
            else:
                return img, masks_array, d, detail_num
        return img, masks_array, d, detail_num + 1


    def main_job(self):
        print(os.getcwd() + "\n")
        output = open(f'step 3 output.txt', 'w+')
        name_back = self.backgrounds + '/' + str(1) + ".jpg"
        img = cv2.imread(name_back)
        start = time.time()
        for id in range(10000):
            k = int(random.uniform(1, 63))  # номер фона
            if k > 50:
                k = 51  # фотография пустого стола под номером 51
            name_back = self.backgrounds + '/'+ str(k) + ".jpg"
            background = resize_specific_width_and_height(cv2.imread(name_back), 1920, 1080)
            masks_array = np.zeros((1080 * 1920 * 20)).reshape((1080, 1920, 20))
            start_time = time.time()
            a = int(random.uniform(1, len(self.all_details_names)))  # количество деталей на картинке
            output.write(f'amount of details is {a} for img_{id}\n')
            print(f'amount of details is {a} for img_{id}\n')
            detail_num = 0
            while detail_num < a:
                print(f'detail_num: {detail_num}')
                if detail_num <= 0:
                    d = {}
                j = int(random.uniform(0, len(self.all_details_names)))  # номер детали из комплекта
                detail_name = self.all_details_names[j]
                # print(detail_name)
                if detail_name == "hand":
                    print('1')
                    detail_path, mask_path = get_hand_path(detail_name, self.all_details_names)
                    print('2')
                    # cv2.imshow(str("1"), cv2.imread(detail_path))
                    # cv2.waitKey(0)
                    # cv2.imshow(str("2"), cv2.imread(mask_path))
                    # cv2.waitKey(0)
                else:
                    print('3')
                    detail_path, mask_path = get_detail_path(self.processed_path, detail_name, self.all_details_names)
                    print('4')
                output.write(f'{detail_path}\n')
                vf = int(random.uniform(0, 2))
                hf = int(random.uniform(0, 2))
                vf = int(random.uniform(0, 2))
                rot = int(random.uniform(0, 360))
                print('biba')
                img, masks_array, d, detail_num = self.generate_new_photo(detail_num, id, detail_name, img, detail_path, mask_path,
                                                    background, masks_array, count=a, d=d, vert_flip=vf, horiz_flip=hf, rot=rot)
            file_name = f'img_{id}'
            write_yolo_txt(d, file_name, a)
            cv2.imwrite(f'{self.generated_images}/{file_name}.jpg', img)
        output.close()
        print("Time:", time.time() - start)


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    bg = BacksGeneration(config)
    bg.main_job()
