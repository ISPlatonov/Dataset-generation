import numpy as np
import os
import cv2
from math import log10
import shutil
#from apply_to_photos import *
from backend.BackgroundImposing.augmentations import *


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


    def generate_mask_name(self, detail, i):
        """
        Генерация имени файла с маской детали.
        :param detail: имя детали
        :param i: номер файла
        :return: name - имя маски
        """
        num_zeros = int(3 - log10(i + 0.1))
        name = self.processed_path + detail + '_' + '0' * num_zeros + str(i) + '/' + detail + '_' + \
            '0' * num_zeros + str(i) + '_detail_bw_mask.jpg'
        return name


    def generate_detail_name(self, detail, i):
        """
        Генерация имени файла с деталью.
        :param detail: имя детали
        :param i: номер файла
        :return: name
        """
        num_zeros = int(3 - log10(i + 0.1))
        name = 'self.processed_path' + detail + '_' + '0' * num_zeros + str(i) + '/' + detail + '_' + \
            '0' * num_zeros + str(i) + '_detail_on_black_bg.jpg'
        return name


    def get_names_of_detail(self, detail):
        """
        Генерация списка с именами файлов масок и фотографий детали
        :param detail: имя детали
        :return: list(1000), list(1000)
        """
        details_names, masks_names = list(), list()
        for i in range(1, 1000):
            details_names.append(self.generate_detail_name(detail, i))
            masks_names.append(self.generate_mask_name(detail, i))
        return details_names, masks_names


    def renaming(self, i, j, detail):
        """
        Непосредственно переименование файлов и удаление директорий.
        :param i: старый номер файла
        :param j: новый номер файла
        :param detail: имя детали
        :return:
        """
        num_zeros1 = '0' * int(3 - log10(i + 0.1))
        num_zeros2 = '0' * int(3 - log10(j + 0.1))
        name1 = f'self.processed_path{detail}_{num_zeros1}{i}/{detail}_{num_zeros1}{i}'
        name2 = f'self.processed_path{detail}_{num_zeros2}{j}/{detail}_{num_zeros2}{j}'
        if not os.path.exists(f'self.processed_path{detail}_{num_zeros2}{j}'):
            os.makedirs(f'self.processed_path{detail}_{num_zeros2}{j}')
        shutil.move(f'{name1}.jpg', f'{name2}.jpg')
        shutil.move(f'{name1}.json', f'{name2}.json')
        shutil.move(f'{name1}_black_and_white_mask.jpg', f'{name2}_black_and_white_mask.jpg')
        shutil.move(f'{name1}_continious_hand_bw_mask.jpg', f'{name2}_continious_hand_bw_mask.jpg')
        shutil.move(f'{name1}_detail_bw_mask.jpg', f'{name2}_detail_bw_mask.jpg')
        shutil.move(f'{name1}_detail_on_black_bg.jpg', f'{name2}_detail_on_black_bg.jpg')
        shutil.move(f'{name1}_hand_on_black_back.jpg', f'{name2}_hand_on_black_back.jpg')
        shutil.move(f'{name1}_landmarks', f'{name2}_landmarks')
        shutil.move(f'{name1}_rect_and_landmarks.jpg', f'{name2}_rect_and_landmarks.jpg')
        shutil.move(f'{name1}_white_countour.jpg', f'{name2}_white_countour.jpg')


    def countour_filtration(self, all_details_names):
        """
        Фильтрация по количеству контуров
        :param all_details_names: список наименований деталей
        :return:
        """
        for i in range(len(all_details_names)):
            count = 0
            detail = all_details_names[i]
            details_names, masks_names = self.get_names_of_detail(detail)
            j = 1
            num_zeros1 = '0' * int(3 - log10(j + 0.1))
            iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
            while iter:
                j += 1
                num_zeros1 = '0' * int(3 - log10(j + 0.1))
                try:
                    iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
                except:
                    j += 1
                    break
                if not iter:
                    print(f'{i + 1})', all_details_names[i], "-", count)
                    break
                detail_path, mask_path = details_names[j - 1], masks_names[j - 1]
                flag = self.filtration(mask_path)
                if flag == 1:
                    count += 1
                    num_zeros1 = '0' * int(3 - log10(j + 0.1))
                    shutil.rmtree(f'self.processed_path{detail}_{num_zeros1}{j}')


    def countour_check(self, all_details_names):
        """
        Проверка по количеству контуров
        :param all_details_names: список наименований деталей
        :return:
        """
        for i in range(len(all_details_names)):
            count = 0
            all_count = 0
            detail = all_details_names[i]
            details_names, masks_names = self.get_names_of_detail(detail)
            j = 1
            num_zeros1 = '0' * int(3 - log10(j + 0.1))
            iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
            while iter:
                all_count += 1
                j += 1
                num_zeros1 = '0' * int(3 - log10(j + 0.1))
                try:
                    iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
                except:
                    j += 1
                    break
                if not iter:
                    break
                detail_path, mask_path = details_names[j - 1], masks_names[j - 1]
                flag = self.filtration(mask_path)
                if flag == 1:
                    count += 1
            print(f'{i + 1}){detail} - {count} / {all_count} ')


    def stop_start_iter(self, detail, j, flag):
        """
        Функция проверки открытия файла
        :param detail: деталь
        :param j: текущий номер
        :param flag: флаг совпадения j и k
        :return: iter, j, flag
        """
        num_zeros1 = '0' * int(3 - log10(j + 0.1))
        iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
        c = 0
        while not iter and j <= 1000:
            j += 1
            c = 1
            num_zeros1 = '0' * int(3 - log10(j + 0.1))
            iter = os.path.exists(f'self.processed_path{detail}_{num_zeros1}{j}')
        if flag == 0 and c > 0:
            flag = 1
        return iter, j, flag


    def counter_files(self, all_details_names):
        """
        Функция подсчета файлов.
        :param all_details_names: список наименований деталей.
        :return:
        """
        for i in range(len(all_details_names)):
            detail = all_details_names[i]
            j = 1
            count = 0
            flag = 0
            iter, j, flag = self.stop_start_iter(detail, j, flag)
            while iter:
                if iter:
                    count += 1
                j += 1
                try:
                    iter, j, flag = self.stop_start_iter(detail, j, flag)
                except:
                    break
                if not iter:
                    print(f'{i + 1})', all_details_names[i], "-", count)
                    break


    def get_prefix_name(self, detail, j):
        num_zeros = '0' * int(3 - log10(j + 0.1))
        name = f'self.processed_path{detail}_{num_zeros}{j}/{detail}_{num_zeros}{j}'
        return name


    def name_proccessing(self, detail, j, k, flag, count2):
        """
        Переименование файлов при выполнении условий с k, j
        :param detail: имя детали
        :param j: номер файла, который переименовываем
        :param k: номер файла, в который переместим
        :param flag: флаг совпадения k и j, т.е. произошел ли сдвиг, была ли пустая директория
        :param count2: счетчик существующих файлов
        :return: k, flag, count2
        """
        name = self.get_prefix_name(detail, j)
        if os.path.exists(f'{name}.jpg') is True and flag == 0:
            k = j
        if k != j and os.path.exists(f'{name}.jpg') is True:
            k += 1
            self.renaming(j, k, detail)
            count2 += 1
        return k, flag, count2


    def name_filtration(self, all_details_names):
        """
        Функция переименования файлов.
        Необходима, когда есть пропущенные или пустые директории.
        :param all_details_names: список наименований деталей
        :return:
        """
        flag = 0
        count2 = 0
        for i in range(len(all_details_names)):
            detail = all_details_names[i]
            j = 0
            print("count2", count2)
            count2 = 0
            k = 1
            iter = True
            while iter:
                j += 1
                try:
                    iter, j, flag = self.stop_start_iter(detail, j, flag)
                except:
                    break
                if not iter:
                    print(f'{i + 1})', detail)
                    break
                if iter:
                    k, flag, count2 = self.name_proccessing(detail, j, k, flag, count2)
            for ost in range(k + 1, j):  # удаляем лишнее
                mydir = f'self.processed_path{all_details_names[i]}_{ost}'
                try:
                    shutil.rmtree(mydir)
                except OSError as e:
                    continue
                    # print("Error: %s - %s." % (e.filename, e.strerror))
            print(f'{i})', all_details_names[i], "-", count2)
            flag = 0


    def main_job(self):
        self.name_filtration(self.all_details_names)
        self.countour_filtration(self.all_details_names)
        # counter_files(all_details_names)
        self.name_filtration(self.all_details_names)
        self.countour_check(self.all_details_names)


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    filt = Filtration(config)
    filt.main_job()
