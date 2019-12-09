
import numpy as np
import math
from fractions import Fraction
import cv2

#// daqui pra baixo são umas variáveis que são necessárias para o processamento, algumas delas só serão usadas aqui, outras não.
#// tem-se de ver onde elas ficarão para saber se necessitará ou não explicitar, dentro de uma função, se elas são globais
#// do jeito que eu testei, que foi com elas assim, e só precisei explicitar, em process(), que "torradas_all" é global

# Dimensões Imagem
M = 720
N = 1280

# Regiao Processamento Start
xe = 100

# Regiao Processamento End
xd = 250

# Parametro usado para saber se deve colocar ou não a torrada na lista, ver eh_nova()
lim = 20 #//eu não sei explicar isso... mas só funciona assim... tô confiando no Esteves, pq ele pediu =)

# Angulo onde as torradas são consideradas dentro do padrão
alfa = 0.0
# Velocidade  do vídeo, em pixels/frame, que é fornecida externamente
vel = 3.46
# lista com todas as torradas, que será passado para a interface, esta é a variável de retorno da função process()
torradas_all = []

# Nº de torradas totais fora do padrão, nº de torradas atualmente na esteira que estão fora do padrão 
total_t = 0

att_t = 0

#// ^ variáveis necessárias para as funções


#Classe para as torradas
class Torrada:
    
    def __init__(self, box=0, angulo=0, centroide=[], vel=3.46):
        self.box = box
        self.ang = angulo
        self.centroide = centroide
        self.velocidade = vel
        self.shift = self.calc_shift(vel)
    
    def get_box(self):
        return self.box
    
    def get_angulo(self):
        return self.ang
    
    def get_centroide(self):
        return self.centroide
    
    def get_velocidade(self):
        return self.velocidade
    
    def get_shift(self):
        return self.shift
    
    def set_box(self, box):
        self.box = box
    
    def set_centroide(self, centroide):
        self.centroide = centroide
    
    def set_velocidade(self, velocidade):
        self.velocidade = velocidade
    
    def set_shift(self, shift):
        self.shift = shift

    def serialize(self):
        return [self.centroide[0], self.centroide[1], self.ang]
            
    def calc_shift(self, velocidade):
    
        teto = math.ceil(velocidade)
        piso = math.floor(velocidade)

        resto = round((velocidade-piso) , 2)

        frac = Fraction(resto).limit_denominator()

        tamanhoProp = frac.denominator  # soma da proporção de nTeto e nPiso
        nTeto = frac.numerator # proporção do teto(ceil)
        nPiso = tamanhoProp - nTeto # proporção do piso(floor)

        array_teto = np.ones(nTeto)*teto
        array_piso = np.ones(nPiso)*piso
                
        output = np.ones(array_teto.size + array_piso.size)
        
        count_teto = 0
        count_piso = 0
        turn_teto = True        
        
        # Intercalando os valores do shift
        for i in range(0,output.size):
            
            if count_teto == array_teto.size:
                output[i] = array_piso[count_piso]
                count_piso = count_piso + 1
                
            elif count_piso == array_piso.size:
                output[i] = array_teto[count_teto]
                count_teto = count_teto + 1
                
            else:
                if turn_teto:
                    output[i] = array_teto[count_teto]
                    count_teto = count_teto + 1
                    turn_teto =  False
                else:
                    output[i] = array_piso[count_piso]
                    count_piso = count_piso + 1
                    turn_teto =  True

        return output


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

        if dist < lim:
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
    global total_t #//necessita saber como ficarão as variáveis, para decidir como vai ficar o código final
    # Encontrando contornos da torrada
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                 
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
            confiavel = eh_confiavel(img, cX, cY)
            
            # Verifica se temos uma nova torrada na area de processamento      
            torrada_nova = eh_nova([cX + xe,cY], prev_torradas)
                     
            if(abs(ang) > alfa and confiavel and torrada_nova):     
                total_t += 1
                # Salvando centroide calculado
                centroide = [cX + xe, cY]
                
                # xe é o offset para o contorno ir para o canto certo
                box[:,0] = box[:,0] + xe
                                
                #Salvando objeto Torrada
                torrada = Torrada(box, ang, centroide, vel)
                
                prev_torradas.append(torrada)
    
    return prev_torradas


def velocidade(cm):
    vel = 0
    # falta ser implementada, ela vai ser usada para calcular, periodicamente, a velocidade da esteira
    # Go Pedros !
    #// a ideia é pegar ela por meio de uma medição externa, e atualizar a variável global vel
    return vel


def process(image):
    global total_t
    global att_t
    _torradas_all = update_torradas(torradas_all)
    _torradas_all = contorno(image, 15, _torradas_all)
    
    att_t = len(_torradas_all)
    ret = []
    for t in _torradas_all:
        ret.append(t.serialize())
    return ret, total_t, att_t
