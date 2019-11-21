import numpy as np
import cv2


def process(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray
