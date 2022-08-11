import random
from math import log10
import os

all_details_names = ("batman", "bolshoy_grover", "bolshoy_podshipnik", "dvernoye_koltso", "grib", "koltso",
                     "krylo", "malenkiy_podshipnik", "nlo", "pruzhina", "roochka", "shesterenka", "sterzhen",
                     "tolstaya_gayka", "tolstaya_shaiba", "tolstoye_koltso", "tonkaya_gayka", "tonkaya_shaiba",
                     "vint", "vtulka")

def get_prefix_name(detail, j):
    """
    Генерация префикса пути к изображению, которое было получено Алексеем
    и положено в папку с соответствующим изображению именем.
    :param detail: str
    :param j: int
    :return:
    """
    num_zeros = '0' * int(3 - log10(j + 0.1))
    name = f'./processed/{detail}_{num_zeros}{j}/{detail}_{num_zeros}{j}'
    return name

def get_detail_path(detail):
    """
    Функция генерации имени файла с изображением и его маски.
    :param detail: str
    :return: str
    """
    i = int(random.uniform(1, 1000))
    name = get_prefix_name(detail, i)
    while not os.path.exists(f'{name}_hand_on_black_back.jpg'):
        i = int(random.uniform(0, len(all_details_names)))
        name = get_prefix_name(detail, i)
    return f'{name}_detail_on_black_bg.jpg', f'{name}_detail_bw_mask.jpg'

def get_hand_path(detail):
    """
        Функция генерации имени файла с изображением руки и его маски.
        :param detail: str
        :return: str
    """
    i = int(random.uniform(1, 1000))
    j = int(random.uniform(0, len(all_details_names)))
    name = get_prefix_name(all_details_names[j], i)
    while not os.path.exists(f'{name}_hand_on_black_back.jpg'):
        i = int(random.uniform(0, len(all_details_names)))
        j = int(random.uniform(1, len(all_details_names)))
        name = get_prefix_name(all_details_names[j], i)
    print(name)
    return f'{name}_hand_on_black_back.jpg', f'{name}_continious_hand_bw_mask.jpg'


