import numpy as np
import cv2


def process(image):
    cv2.imshow('output', image)
    cv2.waitKey(1)
    return image
