import cv2
import json, os


class Dict4Json:

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
        self.names_to_category_id_dict = dict()
        for i in range(len(self.all_details_names)):
            self.names_to_category_id_dict[self.all_details_names[i]] = i + 1    # i + 1?


    def img_with_rectangle(self, img, rect):
        """
        Функция отрисовки прямоугольникоизображении
        :param img: array - изображение
        :param rect: [x1, y1, x2, y2] - np.array
        :return: array
        """
        return cv2.rectangle(img, (rect[0], rect[1]),
                                (rect[2], rect[3]),
                                color=(0, 0, 255), thickness=1)


    def get_category_id(self, detail):
        """
        Функция сопоставления имени детали её номеру
        :param detail: str - name of detail
        :return: int - category_id
        """
        if detail in self.names_to_category_id_dict:
            category_id = self.names_to_category_id_dict[detail]
        else:
            raise Exception("No such name in dict")
        return category_id


    def part_dict(self, id, is_crowd, category_id, yolo_points):
        """
        Функция создания словаря, соотвествующего полю "annotations" в json
        :param id: int - уникальное значение изображения
        :param is_crowd: 1 or 0  - 1 - if true, 0 is false
        :param category_id: int - категория детали
        :param yolo_points: array
        :return: dictionary
        """
        part_dict = {
                    "id": id,
                    "iscrowd": is_crowd,
                    "image_id": id,
                    "category_id": category_id,
                    "segmentation": yolo_points,
                    "yolo": yolo_points,
                    "area": 0.0
                }
        return part_dict


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
        yolo_points = [float(min(x)), float(min(y)), float(max(x)), float(max(y))]
        return yolo_points


    def create_json_dictionary(self, img, file_name, yolo_points, category_id, ID, is_crowd):
        """
        Функция создания json-словаря.
        :param img: image (array)
        :param file_name: str
        :param yolo_points: array
        :param category_id: int
        :param ID: int
        :param is_crowd: 0 or 1
        :return: dictionary
        """
        p = self.part_dict(ID, is_crowd, category_id, yolo_points)
        my_dict = {"info": {"description": "my-project-name"},
                "images": [{ "id": ID, "width": img.shape[1], "height": img.shape[0], "file_name": file_name[31:]}]
                }
        my_dict["annotations"] = []
        my_dict["annotations"].append(p)
        return my_dict


    def edit_json_dictionary(self, my_dict, flag, id, is_crowd, category_id, yolo_points, names_list):
        """
        Функция редактирования словаря: добавление поля annotations.
        :param my_dict: dictionary
        :param flag: int (0 or 1)
        :param id: int
        :param is_crowd: int (0 or 1)
        :param category_id: int
        :param yolo_points: array
        :return: dictionary
        """
        if 'annotations' in my_dict:
            my_dict["annotations"].append(self.part_dict(id, is_crowd, category_id, yolo_points))
        else:
            my_dict["annotations"] = []
            my_dict["annotations"].append(self.part_dict(id, is_crowd, category_id, yolo_points))
        if flag == 1:
            labels = list()
            for i in range(len(names_list)):
                labels.append({'id':str(i), 'name': names_list[i]})
            #labels.append({'id':str(len(names_list)), 'name': 'hand'})
            my_dict["categories"] = labels
        return my_dict


    def writing_in_json(self, detail_num, img, detail_name, id, approx, count, d, names_list):
        """
        Функция создания/редактирования словаря - в зависимости от случая.
        :param detail_num: int
        :param img: array
        :param detail_name: str
        :param id: int
        :param approx: array
        :param count: int
        :param d: dictionary
        :return:  dictionary
        """
        print(f'names_list: {names_list}')
        is_crowd = 0
        if count > 1:
            is_crowd = 1
        dir_name = 'generated_images_json'
        try:
            os.mkdir(dir_name)
        except FileExistsError:
            pass
        file_name = f'{dir_name}/img_{id}.jpg'
        category_id = self.get_category_id(detail_name)
        yolo_points = approx
        if detail_num <= 0:
            d = self.create_json_dictionary(img, file_name, yolo_points, category_id, id, is_crowd)
        else:
            flag = 0
            if detail_num + 1 == count:
                flag = 1
            self.edit_json_dictionary(d, flag, id, is_crowd, category_id, yolo_points, names_list)
        with open(f'{dir_name}/img_{id}.json', 'w') as outfile:
            json.dump(d, outfile)
        return d


    def write_yolo_txt(self, d, file_name, a):
        """
        Функция создания текстовых файлов с разметкой для йолы.
        :param d: dictionary
        :param file_name: str
        :param a: int - количество деталей на изображении
        :return:
        """
        dir_name = 'yolo_points'
        try:
            os.mkdir(dir_name)
        except FileExistsError:
            pass
        f = open(f'{dir_name}/{file_name}.txt', 'w+')
        for i in range(a):
            string = str(d["annotations"][i]["category_id"]) + ' ' + \
                    str(d["annotations"][i]["yolo"][0]) + ' ' + \
                    str(d["annotations"][i]["yolo"][1]) + ' ' + \
                    str(d["annotations"][i]["yolo"][2]) + ' ' + \
                    str(d["annotations"][i]["yolo"][3]) + '\n'
            f.write(string)
            # img = img_with_rectangle(img, d["annotations"][i]["yolo"])
        f.close()
