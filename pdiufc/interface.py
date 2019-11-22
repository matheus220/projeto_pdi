import numpy as np
import cv2


def process(processed_data, original_image):
    cv2.imshow('output', processed_data)
    cv2.waitKey(1)
