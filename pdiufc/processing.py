import numpy as np
import cv2


def process(image):
    cv2.circle(image, (300,200), 100, (255,255,255), thickness=-1)
    return image
