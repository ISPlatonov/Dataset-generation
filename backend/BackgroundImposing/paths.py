import random
import os


def get_detail_path(detail_name, back_directory):
    """
    Функция генерации имени файла с изображением и его маски.
    """
    detail_folder = random.choice([x for x in os.listdir(back_directory) if x.find(detail_name) != -1])
    name = back_directory + '/' + detail_folder + '/' + detail_folder
    return f'{name}_roi.jpg', f'{name}_roi.jpg' 

def get_shuffle_detail_path(i_mask, all_masks_folders, back_directory):
    i = int(i_mask / 4)
    name = back_directory + all_masks_folders[i] + '/' + all_masks_folders[i]
    detail_name = all_masks_folders[i][:all_masks_folders[i].rfind('_')]
    # rotation
    return f'{name}_roi.jpg', detail_name

def get_hand_path(i, all_hand_folders, back_directory):
    """
        Функция генерации имени файла с изображением руки и его маски.
        :param detail: str
        :return: str
    """
    name = back_directory + all_hand_folders[i] + '/' + all_hand_folders[i]
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
