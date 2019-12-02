from skimage.filters import median
from skimage.morphology import disk
import cv2

def preprocess(image):
    # FILTRO DE MÉDIA PARA BORRAR BACKGROUND
    blur15 = cv2.blur(image[:,:,1],(10,10))
    # LIMIARIZAÇÃO
    ret,thresh1 = cv.threshold(image[:,:,1],160,255,cv.THRESH_BINARY)
    # FILTRO DE MEDIANA PARA ELIMINAR RUÍDO SAL-E-PIMENTA RESIDUAL
    med = median(thresh1, disk(5))
    return med

