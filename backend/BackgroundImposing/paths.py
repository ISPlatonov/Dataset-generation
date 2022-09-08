import random
from math import log10
import os


def get_prefix_name(processed_path, detail, j):
    """
    Генерация префикса пути к изображению, которое было получено Алексеем
    и положено в папку с соответствующим изображению именем.
    :param detail: str
    :param j: int
    :return:
    """
    num_zeros = '0' * int(3 - log10(j + 0.1))
    name = f'{processed_path}/{detail}_{num_zeros}{j}/{detail}_{num_zeros}{j}'
    return name


def get_detail_path(processed_path, detail, all_details_names):
    """
    Функция генерации имени файла с изображением и его маски.
    :param detail: str
    :return: str
    """
    print(f'processed_path: {processed_path}, detail: {detail}')
    import re
    photos = os.listdir(processed_path)
    name_regex = re.compile('^' + detail + '\_\d{3}$')
    detail_files = [photo for photo in photos if name_regex.match(photo)]
    print(f'detail files: {detail_files}')
    #i = int(random.uniform(1, len(detail_files)))
    detail_folder = random.choice(detail_files)
    name = f'{processed_path}/{detail_folder}/{detail_folder}'
    print(f'name: {name}')
    #i = int(random.uniform(1, 1000))
    #print('31')
    #name = get_prefix_name(processed_path, detail, i)
    #print(f'name: {name}')
    #while not os.path.exists(f'{name}_hand_on_black_back.jpg'):
    #    i = int(random.uniform(0, len(all_details_names)))
    #    name = get_prefix_name(processed_path, detail, i)
    #    #print(f'name: {name}')
    return f'{name}_detail_on_black_bg.jpg', f'{name}_detail_bw_mask.jpg'


def get_hand_path(detail, all_details_names):
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
