import random
import os


def get_detail_path(detail_name, back_directory):
    """
    Функция генерации имени файла с изображением и его маски.
    """
    detail_folder = random.choice([x for x in os.listdir(back_directory) if x.find(detail_name) != -1])
    name = back_directory + '/' + detail_folder + '/' + detail_folder
    return f'{name}_roi.jpg', f'{name}_roi.jpg'  # f'{name}_detail_on_black_bg.jpg', f'{name}_detail_bw_mask.jpg'


def get_hand_path(back_directory):
    """
        Функция генерации имени файла с изображением руки и его маски.
        :param detail: str
        :return: str
    """
    detail_folder = random.choice(os.listdir(back_directory))
    name = back_directory + '/' + detail_folder + '/' + detail_folder
    return f'{name}_hand_on_black_back.jpg', f'{name}_continious_hand_bw_mask.jpg'

def get_dst_path(back_directory):
    """
    Функция генерации имени файла с изображением и его маски.
    """
    detail_folder = random.choice(os.listdir(back_directory))
    name = back_directory + '/' + detail_folder + '/' + detail_folder
    return f'{name}_dst.jpg'

def preparing_dirs():
    if not os.path.exists('./generated_images_json'):
        os.mkdir('./generated_images_json')
    if not os.path.exists('./generated_images'):
        os.mkdir('./generated_images')
    if not os.path.exists('./yolo_points'):
        os.mkdir('./yolo_points')
