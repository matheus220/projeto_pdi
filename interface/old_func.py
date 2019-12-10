import cv2
import numpy as np
import math
xe = 100
y1 = 0; y2 = 700
xd = 270
    ## ang e contorno calculam o angulo pelo retângulo gerado por cv2.boxPoints()
def angTor( Box , Centro):
    angulo = 0
    if( (Box[0][0] > Centro[0]) ):
        #tipo 1
        x = Box[3][0] - Box[0][0]
        if(x):
            y = Box[3][1] - Box[0][1]
            angulo = math.degrees(math.atan(y/x))
            angulo = 90 + angulo
    elif( (Box[0][0] < Centro[0]) ):
        #tipo2
            x = Box[0][0] - Box[1][0]
            if(x):
                y = Box[1][1] - Box[0][1]
                angulo = math.degrees(math.atan(y/x))
                angulo = -1*(angulo + 90)
    return round(angulo,2)
##########################
def contorno(img, alfa):
    imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgG, 140, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        rect = cv2.minAreaRect(contours[i])
        M = cv2.moments(contours[i])
        if(int(M["m00"])):
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            box = cv2.boxPoints(rect)

            box = np.int0(box)
            ang =  angTor(box,[cX,cY])
            if(abs(ang) >= alfa and float(rect[1][1] > 50) and float(rect[1][0] > 50) ):
                font = cv2.FONT_HERSHEY_SIMPLEX
                pos = ( box[0][0], box[0][1] )
                cv2.putText(img,str(ang),pos, font, 0.8,(0,0,255),2,cv2.LINE_AA)

                img = cv2.drawContours(img,[box],-1,(0,255,200),2)

    return img

    ## ang2 e contorno2 usam o angulo de cv2.minAreaRect()

def angTor2( Box , Centro, ang):
    angulo = 0
    if( (Box[0][0] > Centro[0]) ):
        #tipo 1
        angulo = 90 + ang
    else:
        angulo = ang
    return round(angulo,2)
##########################
def contorno2(img, img_original, alfa):
    imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgR = imgG[:,xe:xd:1]
    ret, thresh = cv2.threshold(imgR, 140, 255, 0)
    try:
        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        rect = cv2.minAreaRect(contours[i])
        M = cv2.moments(contours[i])
        if(int(M["m00"])):
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            box = cv2.boxPoints(rect)
            box = np.int0(box)

            a = float(rect[2])
            ang =  angTor2(box,[cX,cY],a)
            if(abs(ang) >= alfa and float(rect[1][1] > 50) and float(rect[1][0] > 50)):
                # 100 é o offset para o contorno ir para o canto certo
                box[:,0] = box[:,0] + 100

                font = cv2.FONT_HERSHEY_SIMPLEX
                pos = ( box[0][0], box[0][1] )
                cv2.putText(img_original,str(ang),pos, font, 0.8,(0,0,255),2,cv2.LINE_AA)

                img = cv2.drawContours(img_original,[box],-1,(0,255,200),2)

    return img