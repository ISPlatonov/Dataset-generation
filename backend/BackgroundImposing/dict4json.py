import cv2
import json

def img_with_rectangle(img, rect):
    """
    Функция отрисовки прямоугольникоизображении
    :param img: array - изображение
    :param rect: [x1, y1, x2, y2] - np.array
    :return: array
    """
    return cv2.rectangle(img, (rect[0], rect[1]),
                              (rect[2], rect[3]),
                              color=(0, 0, 255), thickness=1)

labels = [{"id": 1, "name": "batman"}, {"id": 2, "name": "bolshoy_grover"},
              {"id": 3, "name": "bolshoy_podshipnik"}, {"id": 4, "name": "dvernoye_koltso"},
              {"id": 5, "name": "grib"}, {"id": 6, "name": "koltso"},
              {"id": 7, "name": "krylo"}, {"id": 8, "name": "malenkiy_podshipnik"},
              {"id": 9, "name": "nlo"}, {"id": 10, "name": "pruzhina"},
              {"id": 11, "name": "roochka"}, {"id": 12, "name": "shesterenka"},
              {"id": 13, "name": "sterzhen"}, {"id": 14, "name": "tolstaya_gayka"},
              {"id": 15, "name": "tolstaya_shaiba"}, {"id": 16, "name": "tolstoye_koltso"},
              {"id": 17, "name": "tonkaya_gayka"}, {"id": 18, "name": "tonkaya_shaiba"},
              {"id": 19, "name": "vint"}, {"id": 20, "name": "vtulka"}, {"id": 21, "name": "hand"}]

def get_category_id(detail):
    """
    Функция сопоставления имени детали её номеру
    :param detail: str - name of detail
    :return: int - category_id
    """
    names_to_category_id_dict = {"batman": 1, "bolshoy_grover": 2,
                                 "bolshoy_podshipnik": 3, "dvernoye_koltso": 4,
                                 "grib": 5, "koltso": 6,
                                 "krylo": 7, "malenkiy_podshipnik": 8,
                                 "nlo": 9, "pruzhina": 10,
                                 "roochka": 11, "shesterenka": 12,
                                 "sterzhen": 13, "tolstaya_gayka": 14,
                                 "tolstaya_shaiba": 15, "tolstoye_koltso": 16,
                                 "tonkaya_gayka": 17, "tonkaya_shaiba": 18,
                                 "vint": 19, "vtulka": 20, "hand": 21}
    if detail in names_to_category_id_dict:
        category_id = names_to_category_id_dict[detail]
    else:
        raise Exception("No such name in dict")
    return category_id

def part_dict(id, is_crowd, category_id, yolo_points):
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

def get_yolo_points(points):
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

def create_json_dictionary(img, file_name, yolo_points, category_id, ID, is_crowd):
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
    p = part_dict(ID, is_crowd, category_id, yolo_points)
    my_dict = {"info": {"description": "my-project-name"},
               "images": [{ "id": ID, "width": img.shape[1], "height": img.shape[0], "file_name": file_name[31:]}]
              }
    my_dict["annotations"] = []
    my_dict["annotations"].append(p)
    return my_dict

def edit_json_dictionary(my_dict, flag, id, is_crowd, category_id, yolo_points):
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
        my_dict["annotations"].append(part_dict(id, is_crowd, category_id, yolo_points))
    else:
        my_dict["annotations"] = []
        my_dict["annotations"].append(part_dict(id, is_crowd, category_id, yolo_points))
    if flag == 1:
        my_dict["categories"] = labels
    return my_dict

def writing_in_json(detail_num, img, detail_name, id, approx, count, d):
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
    is_crowd = 0
    if count > 1:
        is_crowd = 1
    dir_name = 'D:/generated_images_json/'
    file_name = f'{dir_name}img_{id}.jpg'
    category_id = get_category_id(detail_name)
    yolo_points = approx
    if detail_num <= 0:
        d = create_json_dictionary(img, file_name, yolo_points, category_id, id, is_crowd)
    else:
        flag = 0
        if detail_num + 1 == count:
            flag = 1
        edit_json_dictionary(d, flag, id, is_crowd, category_id, yolo_points)
    with open(f'{dir_name}img_{id}.json', 'w') as outfile:
        json.dump(d, outfile)
    return d

def write_yolo_txt(d, file_name, a):
    """
    Функция создания текстовых файлов с разметкой для йолы.
    :param d: dictionary
    :param file_name: str
    :param a: int - количество деталей на изображении
    :return:
    """
    f = open(f'D:/yolo_points/{file_name}.txt', 'w+')
    for i in range(a):
        string = str(d["annotations"][i]["category_id"]) + ' ' + \
                 str(d["annotations"][i]["yolo"][0]) + ' ' + \
                 str(d["annotations"][i]["yolo"][1]) + ' ' + \
                 str(d["annotations"][i]["yolo"][2]) + ' ' + \
                 str(d["annotations"][i]["yolo"][3]) + '\n'
        f.write(string)
        # img = img_with_rectangle(img, d["annotations"][i]["yolo"])
    f.close()
