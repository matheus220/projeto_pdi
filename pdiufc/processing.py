
import numpy as np
import math
from fractions import Fraction
import cv2

#// esta
# Torrada objeto
torrada = Torrada()

# Dimensões Imagem
M = 720
N = 1280

# Regiao Processamento Start
xe = 100

# Regiao Processamento End
xd = 250

# Angulo onde as torradas são consideradas dentro do padrão
alfa = 0.0
# lista com todas as torradas, que será passado para a interface, esta é a variável de retorno da função process()
torradas_all = []


# angTor() calcula o angulo de rotação da torrada a partir do Box retornado pela função do OpenCV
def angTor( Box , Centro, ang):
    angulo = 0
    if( (Box[0][0] > Centro[0]) ):
        #tipo 1
        angulo = 90 + ang
    else:
        angulo = ang
    return round(angulo,2)


# eh_confiavel verifica se na região de processamento tem uma torrada inteira
def eh_confiavel(img, centroide_x, centroide_y):
     
    direita_ok = False
    esquerda_ok = False
    
    if img[centroide_y, centroide_x] == 0.0:
        return False
            
    for i in range(centroide_x, xd-xe):
        if img[centroide_y, i] == 0.0:
            direita_ok = True
            break
            
    for i in range(centroide_x, -1, -1):
        if img[centroide_y, i] == 0.0:
            esquerda_ok = True
            break
    
    if direita_ok and esquerda_ok:
        return True
    else:
        return False   

# Checa se uma torrada é nova, utilizada para saber se é para dar append() em torradas_all
def eh_nova(centroide_atual, torradas):
    is_nova = True
    
    
    for torrada in torradas:
        centroide = torrada.get_centroide()
        
        dist = math.sqrt((centroide[0] - centroide_atual[0])**2 + (centroide[1] - centroide_atual[1])**2)

        if dist < 150:
            is_nova = False
            break
            
    return is_nova


# Após as torradas serem identificadas e colocadas na lista torradas_all, update_torradas() atualiza elas para manter registro das mesmas
# até fora da zona de processamento
def update_torradas(all_torradas):
    
    
    if len(all_torradas) == 0:
        return all_torradas
    
    for torrada in all_torradas:
        box = torrada.get_box()
        centroide = torrada.get_centroide()
        
        shift = torrada.get_shift()
        
        new_shift = np.roll(shift, 1)
        
        torrada.set_shift(new_shift)
            
        box[:,0] = box[:,0] + shift[0]
        centroide[0] = centroide[0] + shift[0]
              
        if centroide[0] >= 1280:
            all_torradas.remove(torrada)
        else:
            torrada.set_box(box)
            torrada.set_centroide(centroide)
    
    return all_torradas

# contorno() atualmente pega o contorno das torradas alvo ( rotação > alfa) e as destaca na imagem,
# porém o objetivo é retornar uma lista com o centro de massa e a rotação das torradas alvo. Go Esteves!
def contorno(img, alfa, prev_torradas):
    
    imgG = cv2.cvtColor(img[:,xe:xd:1], cv2.COLOR_BGR2GRAY) 
    imgR = imgG
    ret, thresh = cv2.threshold(imgR, 140, 255, 0)
    
    # Encontrando contornos da torrada
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                 
    num_torradas = len(contours)
    
    # Executando operações para cada torrada inclionada encontrada
    for i in range(num_torradas):
        
        # Elementos da tupla rect -> 0: (x,y); 1: (width,height); 2: angulo
        # Gerando pontos de contorno da torrada
        rect = cv2.minAreaRect(contours[i])
        
        # Obtendo momentos a partir do contorno da torrada
        M = cv2.moments(contours[i])
                
        # Checando divisão por zero
        if(int(M["m00"])):
            
            # Calculando Centroide
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        
            # Gerando contorno da torrada a partir dos pontos gerados
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            # Ajuste do angulo calculado da torrada
            # minAreaRect() retorna apenas angulos entre -0 e -90
            a = float(rect[2])
            ang =  angTor(box,[cX,cY],a)
            
            torrada_width = rect[1][0]
            torrada_height = rect[1][1]
            
            # Verifica se a torrada está totalmente na região de processamento
            confiavel = eh_confiavel(thresh, cX, cY)
            
            # Verifica se temos uma nova torrada na area de processamento      
            torrada_nova = eh_nova([cX,cY], prev_torradas)
                     
            if(abs(ang) > alfa and confiavel and torrada_nova):     
                                
                # Salvando centroide calculado
                centroide = [cX + xe, cY]
                
                # xe é o offset para o contorno ir para o canto certo
                box[:,0] = box[:,0] + xe
                                
                #Salvando objeto Torrada
                velocidade = 3.46
                torrada = Torrada(box, ang, centroide, velocidade)
                
                prev_torradas.append(torrada)
    
    return prev_torradas

def velocidade(cm):
    vel = 0
    # falta ser implementada, ela vai ser usada para calcular, periodicamente, a velocidade da esteira
    # Go Pedros !
    #// a ideia é pegar ela por meio de uma medição externa, e atualizar a variável global vel
    return vel

# width e height devem ser parametros opcionais, para a área de processamento da imagem, caso não sejam passados,
# os valores padrão estão definidos abaixo dos imports(para a altura, é toda a imagem) ... ainda falta implementá-los
def process(image,alfa):
    global torradas_all
    torradas_all = update_torradas(torradas_all)
    torradas_all = contorno(teste, alfa, torradas_all)
    return torradas_all
