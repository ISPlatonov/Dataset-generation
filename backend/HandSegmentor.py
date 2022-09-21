import cv2
import mediapipe as mp  # библиотека для отслеживания рук
import os
import numpy as np
import json
from PIL import ImageStat
import PIL
from pycocotools.coco import COCO
from threading import Thread, active_count
from PySide6.QtCore import Signal


class HandSegmentor:

    def __init__(self, config):
        self.filepath =  config["filepath"] # для тестирования на конкретном фото
        self.filename = config["filename"]  # для тестирования на конкретном фото
        # путь до эталонного фото пустого стола
        self.empty_table_filepath_to_folder_ = self.filepath + 'Blank_surface/'
        self.empty_table_photo_name_ = config["empty_table_photo_name_"]
        # путь для записи папок с сгенерировнными json файлами и промежуточными масками
        self.output_dir = self.filepath + 'processed/'
        # для тестирования на конкретном фото
        self.root_dir_with_dirs = self.filepath
        self.processed_dir = self.filepath + 'processed'
        self.need_hand = config["need_hand"]
        self.min_roi_height = config["roi"]["height"]
        self.min_roi_width = config["roi"]["width"]
        names_list = os.listdir(self.filepath)
        if 'backgrounds' in names_list:
            names_list.remove('backgrounds')
        if 'Blank_surface' in names_list:
            names_list.remove('Blank_surface')
        if 'processed' in names_list:
            names_list.remove('processed')
        if '.gitignore' in names_list:
            names_list.remove('.gitignore')
        if 'generated_images' in names_list:
            names_list.remove('generated_images')
        self.labels = list()
        for i in range(len(names_list)):
            self.labels.append({'id':str(i), 'name': names_list[i]})
        self.labels.append({'id':str(len(names_list)), 'name': 'hand'})


    def main_job(self, signal, increment_hsStatus):
        try:
            os.makedirs(self.processed_dir)
        except:
            pass
        # для обрабокти всей папки с подпапками с фото
        photo_num = 0
        for i in range(len(self.labels) - 1):
            my_path = self.root_dir_with_dirs + self.labels[i]["name"] + "/"
            photo_num += len(os.listdir(my_path))
        increment = 1 / photo_num
        for i in range(len(self.labels) - 1):
            my_path = self.root_dir_with_dirs + self.labels[i]["name"] + "/"
            for filename_batch in self.batch(os.listdir(my_path), os.cpu_count() - active_count()):
                thread_batch = list()
                for filename in filename_batch:
                    if filename[filename.rfind(".") + 1:] in ['jpg', 'png']:
                        cur_detail_path = my_path + filename   # !!!
                        thread_batch.append(Thread(
                                                target=self.mediapipe_hand_track,
                                                args=(cur_detail_path, filename, self.output_dir,
                                                self.empty_table_filepath_to_folder_,
                                                self.empty_table_photo_name_,),
                                                kwargs={'eps': 100, 'show': False, 'save': True,
                                                'need_hand': self.need_hand,
                                                'increment_hsStatus': increment_hsStatus,
                                                'increment': increment})
                                           )
                for thread in thread_batch:
                    thread.start()
                for thread in thread_batch:
                    thread.join()
                thread_batch.clear()
        # папка со сгенерированными json файлами
        self.unite_many_jsons(self.processed_dir, self.labels)
        #unite_many_jsons_condition(test_dir, all_imgs_in_one_dir_together, labels)
        #delete_files_without_segmentation(all_imgs_in_one_dir_together)
        signal.emit()
    

    def batch(self, iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

        
    # ID надо сделать членом класса -> уникальность
    def json_dictionary(self, file_name, points, x_min, y_min, x_max, y_max, eps1=70, eps2=5, ID=0, is_crowd=0):
        """
        Создание и заполенение одного json файла для конкретной фотографии (на фото один объект с рукой)
        :param labels: словарь меток классов распознаваемых объектов
        :param file_name: имя конкретного файла (фото), например "batman_002.jpg"
        :param points: массив точек [x1, y1, x2, y2,...], аппроксимирующих границы изображения
        :param x_min: x координата левого верхнего угла прямоугольника для обхъекта "рука"
        :param y_min: y координата левого верхнего угла прямоугольника для обхъекта "рука"
        :param x_max: x координата правого нижнего угла прямоугольника для обхъекта "рука"
        :param y_max: y координата правого нижнего угла прямоугольника для обхъекта "рука"
        :param eps1: величина "растяжения" прямоугольника вокруг руки
        :param eps2: величина "растяжения" прямоугольника вокруг детали
        :param ID: уникальное значение изображения (у нас один объект в кадре, поэтому 0)
        :param is_crowd: 0 сегментация основывается на многоугольнике
        :return: my_dict: заполненный словарь для записи в json
                yolo_points_detail: прямоугольник для yolo [x1, y1, x2, y2]
        """
        names_to_category_id_dict = dict()
        for item in self.labels:
            names_to_category_id_dict[item["name"]] = item["id"]
        # проверка корректности переданного имени изображения, что оно есть в исходном словаре
        print('orig. name: ' + file_name + ', for json file_name: ' + file_name[:-file_name[::-1].find('_')-1])
        if file_name[:-file_name[::-1].find('_')-1] in names_to_category_id_dict:
            category_id = names_to_category_id_dict[file_name[:-file_name[::-1].find('_')-1]]
        else:
            raise Exception("Такого имени нет в словаре!")
        hand_category_id = names_to_category_id_dict["hand"]  # считываем id руки
        x, y, arr_x, arr_y = [], [], [], []
        for i in range(points.shape[0]):
            x.append(float((points[:][i][0])[0] + x_min))  # выделили только х из переданного массива
            y.append(float((points[:][i][0])[1] + y_min))  # выделили только у из переданного массива
        for i in x:
            arr_x.append(int(i))
        x = arr_x
        for i in y:
            arr_y.append(int(i))
        y = arr_y
        # формируем кординаты прямоугольника для детали, делая отступы
        x1, y1, x2, y2 = int(min(x)) - eps2, int(min(y)) - eps2, int(max(x)) + eps2, int(max(y)) + eps2
        yolo_points_detail = [x1, y1, x2, y2]
        segm_list_detail = [x1, y1, x2, y1, x2, y2, x1, y2]
        # формируем кординаты прямоугольника для руки, делая отступы
        hand_x1, hand_y1, hand_x2, hand_y2 = int(x_min + eps1), int(y_min + eps1), int(x_max - eps1), int(y_max - eps1)
        yolo_points_hand = [hand_x1, hand_y1, hand_x2, hand_y2]
        segm_list_hand = [hand_x1, hand_y1, hand_x2, hand_y1, hand_x2, hand_y2, hand_x1, hand_y2]
        # заполнение массива
        my_dict = {"info": {"description": "my-project-name"},
                "images": [{
                    "id": ID,
                    "width": 1920,
                    "height": 1080,
                    "file_name": file_name  # имя изображения
                }],
                "annotations": [{
                    "id": ID,
                    "iscrowd": is_crowd,  # 1, если истина, 0, если ложь
                    "image_id": ID,  # уникальное значение изображения
                    "category_id": category_id,  # категория детали
                    "segmentation": [segm_list_detail],  # контур детали
                    "bbox": yolo_points_detail,  # точки для обучения yolo (прямоугольник)
                    "area": 0.0  # площадь фигуры внутри segmentation (пока что не предусмотрено данной функцией)
                },
                    {
                        "id": ID + 1,
                        "iscrowd": is_crowd,  # 1, если истина, 0, если ложь
                        "image_id": ID,  # уникальное значение изображения
                        "category_id": hand_category_id,  # категория детали (здесь это рука)
                        "segmentation": [segm_list_hand],  # контур руки
                        "bbox": yolo_points_hand,  # Точки для обучения на руку yolo (прямоугольник)
                        "area": 0.0  # площадь фигуры внутри segmentation (пока что не предусмотрено данной функцией)
                    }
                ],
                "categories": self.labels  # все категории деталей
                }
        ID += 1
        return my_dict, yolo_points_detail


    def mediapipe_hand_track(self, filepath, filename, output_dir, empty_table_filepath_to_folder,
                            empty_table_photo_name, increment_hsStatus, increment, eps=100, show=False, save=False, need_hand=True):
        """
        Функция обработки изображения для выделения детали и руки и записи в json сгенерированных координат
        :param filepath: абсолютный путь до конкретного файла, например r'/Users/alexsoldatov/Desktop/Датасет_20_деталей_
        по_50_штук/batman/batman_002.jpg'
        :param filename: имя конкретного файла (фото), например "batman_002.jpg"
        :param output_dir: дириктория, куда записываются обработанные фото и json, например
        r'/Users/alexsoldatov/Desktop/Датасет_20_деталей_по_50_штук/processed/'
        :param empty_table_filepath_to_folder: путь до изображения пустого стола
        :param empty_table_photo_name: имя фотографии пустого стола
        :param eps: для вырезания области интереса roi немного с запасом
        :param show: bool, вывод промежуточных сохраняемых результатов на экран
        :param save: bool, необходимость сохранения результатов, включая промежуточные
        :return: None
        """
        image_name = filename[:-4]
        empty_table_path = empty_table_filepath_to_folder + empty_table_photo_name
        if empty_table_photo_name not in os.listdir(empty_table_filepath_to_folder):
            raise Exception('Фотография пустого стола не была найдена в папке!')
        img = cv2.imread(filepath)  # считывание текущего изображения
        img_original = img.copy()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # конвертируем в RGB
        x_landmark_coord, y_landmark_coord = [], []

        if need_hand:
            mpHands = mp.solutions.hands  # объект класса для распознавания рук на фотографии
            hands = mpHands.Hands(max_num_hands=5, min_detection_confidence=0.3)
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
                increment_hsStatus(increment)
                return
            x_max, y_max, x_min, y_min = max(x_landmark_coord), max(y_landmark_coord), min(x_landmark_coord), min(
                y_landmark_coord)  # вписываем кисть в прямоугольник
            w, h = x_max - x_min, y_max - y_min
            eps = max(w, h) * 1
            hands.close()  # чистим память
            x_max, y_max, x_min, y_min = x_max + eps, y_max + eps, x_min - eps, y_min - eps  # отступаем от краев
        else:
            x_max, y_max, x_min, y_min = 200, 200, 100, 100
        roi = img_original[y_min:y_max, x_min:x_max]  # выделяем область интереса ROI
        if roi.shape[0] < self.min_roi_height or roi.shape[1] < self.min_roi_width:
            increment_hsStatus(increment)
            return
        YCrCb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCR_CB)  # преобразуем в пространство YCrCb
        (y, cr, cb) = cv2.split(YCrCb)  # выделяем значения Y, Cr, Cb
        cr1 = cv2.GaussianBlur(cr, (5, 5), 0)  # фильтр Гаусса для небольшого размытия
        _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # ostuprocessing
        res = cv2.bitwise_and(roi, roi, mask=skin)
        skin_color = res.copy()
        mask_black_and_white = np.where((res > 0), 0, 255).astype('uint8')
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        dst = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
        Laplacian = cv2.convertScaleAbs(dst)
        h = cv2.findContours(Laplacian, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # находим на изображении контуры
        contour = h[0]
        contour = sorted(contour, key=cv2.contourArea,
                        reverse=True)  # сортируем серию координат точек контура по площади, которую они окружают
        ret_np = np.ones(dst.shape, np.uint8)  # создаем черный занавес
        for i in range(len(contour)):
            ret = cv2.drawContours(ret_np, contour[i], -1, (255, 255, 255), thickness=5)  # Рисуем белый контур
            continious_hand_bw_mask = cv2.drawContours(ret_np, [contour[i]], -1, (255, 255, 255), thickness=-1)
        white_countour = ret.copy()
        empty_table = cv2.imread(empty_table_path)  # считываем фото пустого стола
        empty_table_roi = empty_table[y_min:y_max, x_min:x_max]  # выделяем область интереса ROI
        abs_diff = cv2.absdiff(empty_table_roi, roi)  # делаем разность кадров
        mask_gray = cv2.cvtColor(abs_diff, cv2.COLOR_BGR2GRAY)
        _, diff_thresh = cv2.threshold(mask_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        continious_hand_bw_mask = np.where((continious_hand_bw_mask == 1), 0, 255).astype('uint8')
        mask_inv = cv2.bitwise_not(continious_hand_bw_mask)
        empty_table_fg = cv2.bitwise_and(empty_table_roi, empty_table_roi, mask=continious_hand_bw_mask)
        empty_table_bg = cv2.bitwise_and(empty_table_roi, empty_table_roi, mask=mask_inv)
        hand_fg = cv2.bitwise_and(roi, roi, mask=continious_hand_bw_mask)
        hand_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        dst = cv2.add(empty_table_fg, hand_bg)  # not bad
        dst_copy = dst.copy()
        dst_copy = cv2.cvtColor(dst_copy, cv2.COLOR_BGR2GRAY)
        im = PIL.Image.fromarray(np.uint8(dst_copy))
        mean = ImageStat.Stat(im).mean
        _, bw_mask_thresh = cv2.threshold(dst_copy, mean[0], 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
        bw_mask = cv2.bitwise_and(dst_copy, dst_copy, mask=bw_mask_thresh)
        edged = bw_mask_thresh
        cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # ищем контуры (cv2.RETR_TREE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=False)[:10]  # сортируем контуры по площади контура
        # и выбираем 10 самых больших
        if len(cnts) != 0:
            for c in cnts:
                peri = cv2.arcLength(c, True)  # периметр замкнутых контуров
                approx = cv2.approxPolyDP(c, 0.005 * peri,
                                        True)  # чем коэффициент перед peri больше, тем больше "сравнивание" границ
                # при 0.15 уже может получится квадрат из исходного множества
                # точек, аппроксимирующих шестеренку, в cnts
        else:
            increment_hsStatus(increment)
            return
        # Таким образом, получили массив  approx, приближающих границы маски
        # Далее переведем точки в словарь d и передадим словарь в json-файл "data_file.json"
        d, yolo_points = self.json_dictionary(filename, approx, x_min, y_min, x_max, y_max)
        if show:
            cv2.imshow("img", img)
            cv2.imshow("empty_table_bg", empty_table_bg)
            cv2.imshow("empty_table_fg", empty_table_fg)
            cv2.imshow("hand_bg", hand_bg)
            cv2.imshow("hand_fg", hand_fg)
            cv2.imshow("roi_original", roi)
            cv2.imshow("dst", dst)
            cv2.imshow("dst_copy", dst_copy)
            cv2.imshow("Skin color result", skin_color)
            cv2.imshow("White countour", white_countour)
            cv2.waitKey()
            cv2.destroyAllWindows()
        if save:
            folder_name_path = output_dir + '/{}'.format(image_name)
            try:
                os.makedirs(folder_name_path)
            except OSError as e:
                pass
            cv2.imwrite(folder_name_path + '/{}_rect_and_landmarks.jpg'.format(image_name), img)
            cv2.imwrite(folder_name_path + '/{}_black_and_white_mask.jpg'.format(image_name), mask_black_and_white)
            cv2.imwrite(folder_name_path + '/{}_hand_on_black_back.jpg'.format(image_name), skin_color)
            cv2.imwrite(folder_name_path + '/{}_white_countour.jpg'.format(image_name), white_countour)
            cv2.imwrite(folder_name_path + '/{}_continious_hand_bw_mask.jpg'.format(image_name), continious_hand_bw_mask)
            cv2.imwrite(folder_name_path + '/{}_detail_bw_mask.jpg'.format(image_name), np.array(bw_mask_thresh))
            cv2.imwrite(folder_name_path + '/{}_detail_on_black_bg.jpg'.format(image_name), np.array(bw_mask))
            cv2.imwrite(folder_name_path + '/{}.jpg'.format(image_name), img_original)
            with open(folder_name_path + '/{}.json'.format(image_name), "w") as write_file:  # записываем в файл
                json.dump(d, write_file)  # переводим словарь в формат json
            if need_hand:
                with open(folder_name_path + '/{}'.format(image_name) + '_landmarks', "w") as file1:
                    file1.write(str(results.multi_hand_landmarks))
        increment_hsStatus(increment)
        return


    def unite_many_jsons(self, directory_path, labels):
        """
        Функция, объединяющая json файлы, сгенерированные функцией mediapipe_hand_track в один большой
        json файл
        :param directory_path: абсолютный путь до папки с множеством подпапок с json файлами, например,
        '/Users/alexsoldatov/Desktop/Датасет_20_деталей_по_1000_штук/processed'
        :param labels: словарь меток классов распознаваемых объектов
        :return: None (создает json файл в той же папке)
        """
        my_dict = {"info": {"description": "my-project-name"},
                "images": [],
                "annotations": [],
                "categories": labels  # Все категории деталей
                }
        folder = os.listdir(directory_path)
        annotations_list, images_list = [], []
        for i in range(len(folder)):  # записываем в json файл, пробегаясь по всем папкам
            path = directory_path + '/' + folder[i] + '/'
            if path[path.rfind('.') + 1:-1] in ['json']:
                continue
            for filename in os.listdir(path):
                if filename[filename.rfind(".") + 1:] in ['json']:
                    coco = COCO(path + filename)
                    class_ids = sorted(coco.getCatIds())
                    anns = coco.loadAnns(coco.getAnnIds(
                        imgIds=[0], catIds=class_ids, iscrowd=None))
                    if len(anns) != 2:
                        continue
                    annotations_list.append(anns)
                    images_list.append(coco.loadImgs(ids=[0]))
                    images_list[len(images_list) - 1][0]['id'] = len(images_list) - 1
                    annotations_list[len(annotations_list) - 1][0]['id'] = len(annotations_list) - 1
                    annotations_list[len(annotations_list) - 1][1]['id'] = len(annotations_list) - 1
                    annotations_list[len(annotations_list) - 1][0]['image_id'] = len(annotations_list) - 1
                    annotations_list[len(annotations_list) - 1][1]['image_id'] = len(annotations_list) - 1
        for i in range(len(images_list)):
            my_dict['images'].append(images_list[i][0])
            my_dict['annotations'].append(annotations_list[i][0])
            my_dict['annotations'].append(annotations_list[i][1])
        with open('pack_of_dets_json.json', "w") as write_file:
            json.dump(my_dict, write_file)  # переводим словарь в формат json


    def delete_files_without_segmentation(self, root_dir_with_dirs):
        """
        Функция удаления тех фотографий, которые были удалены из json файла после ручной чистки уже размеченного
        датасета
        :param root_dir_with_dirs: путь до копии всех фотографий в одной папке вместе без подпапок, например,
        r'/Users/alexsoldatov/Desktop/Датасет_20_деталей_по_1000_штук/ALL_imgs_copy(2)/'
        :return: None
        """
        count = 0
        for filename in os.listdir(root_dir_with_dirs):
            # print(root_dir_with_dirs + filename)
            if filename[filename.rfind(".") + 1:] in ['json']:
                coco = COCO(root_dir_with_dirs + filename)
                d = coco.imgs
            if not d:
                return
        for filename in os.listdir(root_dir_with_dirs):
            if filename[filename.rfind(".") + 1:] in ['jpg', 'png']:
                for value in list(d.values()):
                    flag = False
                    if filename == value['file_name']:
                        flag = True
                        break
                if not flag:
                    count += 1
                    os.remove(root_dir_with_dirs + filename)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    hs = HandSegmentor(config)
    hs.main_job()
