import numpy as np
import os
import cv2
import json

class Filtration:

    def __init__(self, config):
        self.processed_path = config['processed_path']
        self.all_details_names = os.listdir(config['filepath'])
        if 'Blank_surface' in self.all_details_names:
            self.all_details_names.remove('Blank_surface')
        if 'processed' in self.all_details_names:
            self.all_details_names.remove('processed')
        if '.gitignore' in self.all_details_names:
            self.all_details_names.remove('.gitignore')


    def get_approx(self, black_and_white_mask):
        """
        Функция получения числа контуров.
        :param black_and_white_mask: маска детали
        :return: np.nan если число контуров < 3. Иначе контур - approx
        """
        mask_gray = black_and_white_mask
        mask_gray = cv2.bilateralFilter(mask_gray, 11, 17, 17)
        cnts, _ = cv2.findContours(mask_gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # or cv2.RETR_TREE
        if len(cnts) > 3 or len(cnts) == 0:
            return np.nan
        cnts = sorted(cnts, key = cv2.contourArea, reverse = False)[:]  # Отсортировали контуры по площади контура
                                                                        # и выбрали все.
        for c in cnts:
            peri = cv2.arcLength(c, True)  # Периметр замкнутых контуров
            approx = cv2.approxPolyDP(c, 0.005 * peri, True)  # Чем коэффициент перед peri больше, тем больше "сравнивание" границ.
                                                            # При 0.15 уже может получится квадрат из исходного множества
                                                            # точек, аппроксимирующих шестеренку, в cnts.
        area = black_and_white_mask.shape[0] * black_and_white_mask.shape[1]
        if cv2.contourArea(approx) / area > 0.23:
            return np.nan

        return approx


    def filtration(self, path_mask):
        """
        Промежуточная функция при фильтрации контуров. Отвечает за то, нужна ли фильтрация или нет
        :param path_mask:
        :return: 0 или 1
        """
        mask = cv2.imread(path_mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        approx = self.get_approx(mask)
        if approx is np.nan:
            return 1
        else:
            return 0


    def countour_filtration(self, all_details_names):
        """
        Фильтрация по количеству контуров
        :param all_details_names: список наименований деталей
        :return:
        """
        for dir in os.listdir(self.processed_path):
            mask_path = f'{self.processed_path}/{dir}/{dir}_detail_bw_mask.jpg'
            flag = self.filtration(mask_path)
            if flag == 1:
                print(f'removing: {dir}')
                for root, dirs, files in os.walk(f'{self.processed_path}/{dir}/'):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(f'{self.processed_path}/{dir}/')


    def empty_dir_filtration(self):
        for dir in os.listdir(self.processed_path):
            if len(os.listdir(f'{self.processed_path}/{dir}/')) == 0:
                os.rmdir(f'{self.processed_path}/{dir}/')


    def main_job(self):
        self.empty_dir_filtration()
        self.countour_filtration(self.all_details_names)
        print(f'Filtration is done!')


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    filt = Filtration(config)
    filt.main_job()
