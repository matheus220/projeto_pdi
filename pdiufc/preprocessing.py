from skimage.filters import median
from skimage.morphology import disk
from skimage.color import rgb2hsv
from skimage import exposure
from scipy.ndimage.morphology import binary_fill_holes
import cv2

def process(image):
    
    #PASSANDO PARA NOVO ESPAÇO DE CORES
    img = rgb2hsv(image)
    # FILTRO DE MÉDIA PARA BORRAR BACKGROUND
    blur15 = cv2.blur(img[:,:,1],(10,10))
    # FILTRO DE MEDIANA PARA ELIMINAR RUÍDO SAL-E-PIMENTA 
    med = median(blur15,disk(5))
    # AJUSTE DE CONSTRASTE
    gamma = exposure.adjust_gamma(med, 2)
    # LIMIARIZAÇÃO
    ret, t = cv2.threshold(gamma,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #PREENCHENDO FALHAS NA TORRADA
    #x = binary_fill_holes(t,structure=np.ones((3,3)))
    #return x
    return t 
