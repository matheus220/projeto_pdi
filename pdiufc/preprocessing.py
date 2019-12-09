from skimage.filters import median
from skimage.morphology import disk
import cv2

def preprocess(image):
    # FILTRO DE MÉDIA PARA BORRAR BACKGROUND
    blur15 = cv2.blur(image[:,:,1],(10,10))
    #blur15 = cv2.GaussianBlur(image[:,:,1],(5,5),8)
    # LIMIARIZAÇÃO
    ret,thresh1 = cv2.threshold(blur15,160,255,cv2.THRESH_BINARY)
    #ret,thresh1 = cv2.threshold(blur15,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # FILTRO DE MEDIANA PARA ELIMINAR RUÍDO SAL-E-PIMENTA RESIDUAL
    med = median(thresh1, disk(5))
    return med
