import random
import cv2
import numpy as np


def resize_specific_width_and_height(img, width, height):
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
    return resized


def scale_image_in_percent(img, relation):
    width = int(img.shape[1] * relation)
    height = int(img.shape[0] * relation)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized


def rotation(img, angle):
    times_90 = angle / 90
    if times_90 > 0:
        img = np.rot90(img, times_90)
    #angle = int(random.uniform(-angle, angle))
    # if angle % 180 == 0:
    #     h, w = img.shape[:2]
    #     M = cv2.getRotationMatrix2D((int(w/2), int(h/2)), angle, 1)
    #     img = cv2.warpAffine(img, M, (w, h))
    # elif angle % 90 == 0:
    #     w, h = img.shape[:2]
    #     M = cv2.getRotationMatrix2D((int(w/2), int(h/2)), angle, 1)
    #     img = cv2.warpAffine(img, M, (w, h))
    return img


def vertical_flip(img, flag):
    if flag:
        return cv2.flip(img, 0)
    else:
        return img


def horizontal_flip(img, flag):
    if flag:
        return cv2.flip(img, 1)
    else:
        return img


def brightness(img, low, high):
    value = random.uniform(low, high)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype = np.float64)
    hsv[:,:,1] = hsv[:,:,1]*value
    hsv[:,:,1][hsv[:,:,1]>255]  = 255
    hsv[:,:,2] = hsv[:,:,2]*value
    hsv[:,:,2][hsv[:,:,2]>255]  = 255
    hsv = np.array(hsv, dtype = np.uint8)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def apply_augmentations(detail, mask, vert_flip=0, horiz_flip=0, rot=0):
    if vert_flip:
        detail = vertical_flip(detail, 1)
        mask = vertical_flip(mask, 1)
    if horiz_flip:
        detail = horizontal_flip(detail, 1)
        mask = horizontal_flip(mask, 1)
    if rotation:
        detail = rotation(detail, rot)
        mask = rotation(mask, rot)
    return detail, mask
