import cv2
import numpy as np
import math
from func import contorno
from func import angTor
from func import contorno2
from func import angTor2
alfa = 0 # alfa é o limiar de angulo para que apareça um contorno

cap = cv2.VideoCapture("fundo_preto_torrada_branca.avi")

count = 0

while True:
    ret, frame = cap.read()
    count = count + 1
    if(ret):
        frame = contorno2(frame,alfa)
        cv2.imshow('frame',frame)
    if(cv2.waitKey(30)!=-1): # aperta ESC e a janela fecha
        break
cap.release()
cv2.destroyAllWindows()