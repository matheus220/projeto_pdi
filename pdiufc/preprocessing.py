
import os
import imageio
import matplotlib.pyplot as plt
from skimage import feature,io
from skimage.feature import canny
import skimage
from skimage.filters import threshold_minimum
from skimage.filters import median
from skimage.morphology import disk


# TRANSFORMANDO O VÍDEO EM ESCALA DE CINZA
reader = imageio.get_reader('video.avi')
fps = reader.get_meta_data()['fps']

writer = imageio.get_writer('gray.mp4', fps=fps)

for im in reader:
    writer.append_data(im[:, :, 1])
writer.close()

# LIMIARIZANDO E ELIMINANDO RUÍDO

filename = 'gray.mp4'
vid = imageio.get_reader(filename,  'ffmpeg')
fps = vid.get_meta_data()['fps'] 


for i, image in enumerate(vid): # Itera sobre frames do vídeo // i
    
    
    if(i<10):
        f = '000' + str(i) + '.png'
    if(i<100 and i >=10):
        f = '00' + str(i) + '.png'
    if(i<1000 and i >=100):
        f = '0' + str(i) + '.png'
    if(i>=1000):
        f = str(i) + '.png'
    
    thresh = threshold_minimum(image[:,:,1])
    binary = image[:,:,1] > thresh
    
    if(i<=17):
        
        edges = canny(image[:, :, 1],sigma = 3)
        plt.imsave(f, edges,cmap = plt.cm.gray)

    if(i>17):        
        med = median(binary, disk(5))
        plt.imsave(f, med,cmap = plt.cm.gray)

os.system('cat *.png | ffmpeg -f image2pipe -framerate 30 -i - output.mkv')

