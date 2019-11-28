import numpy as np
import cv2

xe = 100; xd = 250


# angTor() calcula o angulo de rotação da torrada a partir do Box retornado pela função do OpenCV
def angTor( Box , Centro, ang):
    angulo = 0
    if( (Box[0][0] > Centro[0]) ):
        #tipo 1
        angulo = 90 + ang
    else:
        angulo = ang
    return round(angulo,2)
# contorno() atualmente pega o contorno das torradas alvo ( rotação > alfa) e as destaca na imagem,
# porém o objetivo é retornar uma lista com o centro de massa e a rotação das torradas alvo. Go Esteves!
def contorno(img, alfa): 
    imgG = cv2.cvtColor(img[:,xe:xd:1], cv2.COLOR_BGR2GRAY) # não sei se a imagem já está em cinza...
    imgR = imgG
    ret, thresh = cv2.threshold(imgR, 140, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cXR = 0; cYR = 0
    for i in range(len(contours)):
        rect = cv2.minAreaRect(contours[i])
        #elementos da tupla rect -> 1: (x,y); 2: (width,height); 3: angulo
        M = cv2.moments(contours[i])
        if(int(M["m00"])):
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            a = float(rect[2]) # este é o angulo calculado pela função minAreaRect(), ele está sempre entre -0 e -90, logo precisa ser ajustado
            ang =  angTor(box,[cX,cY],a)
            # " float(rect[1][1] > 50) and float(rect[1][0] > 90 " é para evitar os contornos indesejáveis que são detectados pelo openCV
            if(abs(ang) >= alfa and float(rect[1][1] > 50) and float(rect[1][0] > 90)):
                cXR = cX; cYR = cY
                # 100 é o offset para o contorno ir para o canto certo
                box[:,0] = box[:,0] + 100
                ### Esta parte é apenas para visualizar o que está sendo detectado, não é necessária para a versão final
                font = cv2.FONT_HERSHEY_SIMPLEX
                pos = ( box[0][0], box[0][1] ) 
                cv2.putText(img,str(ang),pos, font, 0.8,(0,0,255),2,cv2.LINE_AA)
                img = cv2.drawContours(img,[box],-1,(0,255,200),2)
                ### Esta parte é apenas para visualizar o que está sendo detectado, não é necessária para a versão final
    return img, [cXR +100, cYR]

def velocidade(cm):
    vel = 0
    # falta ser implementada, ela vai ser usada para calcular, periodicamente, a velocidade da esteira
    # Go Pedros !
    return vel

# width e height devem ser parametros opcionais, para a área de processamento da imagem, caso não sejam passados,
# os valores padrão estão definidos abaixo dos imports(para a altura, é toda a imagem) ... ainda falta implementá-los
def process(image,alfa):
    # cv2.circle(image, (300,200), 100, (255,255,255), thickness=-1) // pra que isso?
    image = contorno(image,alfa)
    return image
