from skimage.filters import median
from skimage.morphology import disk
import cv2

def preprocess(image):
    ret,thresh1 = cv.threshold(image[:,:,1],127,255,cv.THRESH_BINARY)
    med = median(thresh1, disk(5))
    return med

