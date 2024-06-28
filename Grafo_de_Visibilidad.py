# Autor: Baruc Samuel Cabrera Garcia
from vispy import app
import sys
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Polygon, Ellipse, Rectangle, RegularPolygon, Line
from shapely.geometry import Point
from shapely.geometry import Polygon as Polygon_geometry
from vispy.color import Color
import numpy as np
from vispy.visuals.transforms.linear import MatrixTransform
import copy

INF = float('inf')

#Colores 
white = Color("#ecf0f1")
gray = Color("#121212")
red = Color("#e74c3c")
blue = Color("#2980b9")
orange = Color("#e88834")
rosa_hex = Color("#FFC0CB")

#Dimensiones de ventana
scene_width = 700
scene_height = 700

step = np.array([.01, 0.02])
centro = np.array([scene_width/2,scene_height/2])
scale = 1

############################ Funciones
def distancia(A, B):
    #print("----->",A,B)
    return np.sqrt( (B[0] - A[0])** 2 + (B[1] - A[1])**2)


#Considerando un rayo que sale de v_1 a v_2, buscamos alguna intersección 
def interseccion_rectas(v_1, v_2, w_1, w_2):
    """Se asume que las rectas (v_1 , v_2) y (w_1 y w_2) no son paralelas, 
    pero no sabemos si alguna tiene pendiente cero"""
    result = np.array([0,0])

    if (v_1[0] == v_2[0]):#Si la recta (v_1 , v_2) tiene pendiente cero
        x = v_1[0]
        #y = mx + b
        m_w = (w_1[1] - w_2[1]) / (w_1[0] - w_2[0])
        b_w = w_1[1]- (m_w * w_1[0])

        result[0] = x
        result[1] = m_w*x + b_w

    elif (w_1[0] == w_2[0]):#Si la recta (w_1 , w_2) tiene pendiente cero
        x = w_1[0]
        #y = mx + b
        m_v = (v_1[1] - v_2[1]) / (v_1[0] - v_2[0])
        b_v = v_1[1]- (m_v * v_1[0])

        result[0] = x
        result[1] = m_v*x + b_v

    else: #Ninguna recta es de pendiente cero

        #y = mx + b
        m_v = (v_1[1] - v_2[1]) / (v_1[0] - v_2[0])
        b_v = v_1[1] - (m_v * v_1[0])

        m_w = (w_1[1] - w_2[1]) / (w_1[0] - w_2[0])
        b_w = w_1[1]- (m_w * w_1[0])


        result[0] = (b_w - b_v) / (m_v - m_w)
        result[1] = m_v * result[0] + b_v

    distancia_total = distancia(w_1, w_2)
    d1 = distancia(result, w_1)
    d2 = distancia(result, w_2)

    if abs(d1 + d2 - distancia_total) < .1: #Si el resultado esta en la arista
        flag = True
    else:
        flag = False

    return result, flag


def is_parallel(v_1, v_2, w_1, w_2):
    m_v = (v_1[1] - v_2[1]) / (v_1[0] - v_2[0])
    m_w = (w_1[1] - w_2[1]) / (w_1[0] - w_2[0])

    if abs(m_v - m_w) < 0.1 or (abs(m_v) == INF and abs(m_w) == INF):#Para detectar pendientes iguales, o ambas infinitas
        return True
    else:
        return False

def is_in_AB(A,punto,B):#Determina si punto se encuentra en el segmento A,B
    distancia_total = distancia(A, B)
    dA = distancia(punto, A)
    dB = distancia(punto, B)

    if abs(dA + dB - distancia_total) < .1:
        return True
    else:
        return False

def look_for_interseccion(A,B, obstaculo, flag_bitangente = False):
    """
    Dado un rayo que sale de A a B, buscamos determinar 
    si dicho rayo intersecta con alguna arista de obstaculos
    """
    dist_min = INF
    for i in range( len(obstaculo) - 1):
        C = obstaculo[i]
        D = obstaculo[i+1]
        if flag_bitangente:
            print(f"--->Se analizara la arista {A}, {B}")

        if is_parallel(A,B,C,D) == False:#Si AB y CD no son paralelas
            punto, flag = interseccion_rectas(A,B,C,D)#Buscamos su interseccion
            if flag:#Si la interseccion esta en el segmento CD
                d_B = distancia(punto, B)
                d_A = distancia(punto, A)
                if d_B < d_A and d_B != 0:#Si la interseccion esta en la direccion A->B y no es B
                    if d_B < dist_min:#Si este punto es el mas cercano
                        if is_in_AB(A,punto,B) == False:#Si la interseccion no esta entre A y B
                            point_optimo = punto
                            dist_min = d_B

    if dist_min == INF:#Si no encontramos ninguna interseccion en la direaccion A->B
        return B, False
    
    #Si la linea que va de B a point_optimo esta fuera del poligono
    #Para esto utilizamos el punto medio de la supuesta linea formada por B y point_optimo
    poligono = Polygon_geometry(obstaculo)
    punto_medio = (B + point_optimo)/2
    if poligono.contains(Point(punto_medio[0],punto_medio[1])) == False:
        return B, False
    
    return point_optimo, True

#Regresa m,b de y = mx + b
def get_recta_paralela(A,B,C):#Suponemos que C y A no comparten coordenadas X
  ac = C-A #Vector de direccion de C a A
  ac *= 2 #Vector paralelo

  pendiente_m = ac[1]/ac[0] #Pendiente del vector paralelo

  # Calculamos la interseccion b usndo y = mx + b
  b = B[1] - pendiente_m * B[0]  # b = y - mx
  return pendiente_m,b

def share_x(A,C):#Nos dice si A,C comparten coordenadas X
    if A[0] == C[0]:
        return True
    return False

"""Esta funcion sirve para descartar punto si esta en el conjunto V
Se puede adaptar para descartar vertices en general o sharped_vertex segun que conjunto
se ponga"""
def is_in_V(punto, V):
    #print(f"Veremos si {punto} esta en el conjunto {sharped_vertex}")
    return any((punto == vec).all() for vec in V)



def get_point_bitangente(shaped_vertex, obstaculo):
    n_vertex = len(shaped_vertex)

    for i in range(n_vertex):
        v_a = shaped_vertex[i]
        for j in range(n_vertex):
            if j == i:
                continue
            
            v_b = shaped_vertex[j]



            if share_x(v_a, v_b) == False:#Si comparten x, no hay bitangente
                """Imaginemos una recta que una a v_a y v_b, 
                tomamos dos puntos en esa recta fuera del segmento v_a,v_b.
                Uno del lado de v_a y otro del de v_b"""
                #recta que pasa por v_a y v_b p = v_a*t + (1-t)*v_b.

                point_1 = v_a*(1.1) + v_b*(1-1.1)#Lado de a
                point_2 = v_a*(-0.1) + v_b*(1+0.1)#Lado de b

                point_a, flag_a = look_for_interseccion(v_a,point_1, obstaculo)

                point_b, flag_b = look_for_interseccion(v_b,point_2, obstaculo)

                if flag_a:#Si hay interseccion del lado a
                    linea = Line(pos=np.array([v_a, point_a]), color=red, width=2)
                    view.add(linea)                     

                if flag_b:#Si hay interseccion del lado b
                    linea = Line(pos=np.array([v_b, point_b]), color=red, width=2)
                    view.add(linea)



def get_sharp_vertex(obstaculo):#Recibe el conjunto de vertices cerrado
    global view
    # 0 1 2 3 4 5 6 7 8 9 0 (1)
    #Agregamos el vertice 1 para asi poder anaizar los vecinos de los veritces de en medio de aux
    aux = np.concatenate((obstaculo, [obstaculo[1]]))
    n = len(aux)
    sharped_vertex = np.empty((0, 2), dtype=float)

    
    for i in range(1,n-1):
        vertice_a = aux[i-1]
        vertice_b = aux[i]
        vertice_c = aux[i+1]

        p_ab, flag_ab = look_for_interseccion(vertice_a, vertice_b, obstaculo)
        p_cb, flag_cb = look_for_interseccion(vertice_c, vertice_b, obstaculo)

        #Diujamos los rayos de infleccion (si hay)
        if flag_ab:
            linea = Line(pos=np.array([vertice_b, p_ab]), color=white, width=2)
            view.add(linea)
        
        if flag_cb:
            linea = Line(pos=np.array([vertice_b, p_cb]), color=white, width=2)
            view.add(linea)

        if flag_ab and flag_cb:#Guardamos los sharped vertex para dibujar los complementos bitangentes
            sharped_vertex = np.append(sharped_vertex, [vertice_b], axis = 0)


    get_point_bitangente(sharped_vertex, obstaculo)
#############################


canvas = SceneCanvas(keys='interactive', title='Polygon Example',
                     show=True, size = (scene_width, scene_height), autoswap=False, vsync=True)

view = canvas.central_widget.add_view()
view.bgcolor = gray


#Poligono(s) a considerar
vertices_1 = np.array([[100, 100], [500, 100], [550, 250], [500, 400], [450, 400], 
                       [400, 300], [350, 400], [250, 400], [200, 300], [150, 400], 
                       [100, 400], [50, 250], [100, 100]])

vertices_2 = np.array([[200,100], [300,100], [300,200], [400,200], 
                       [400,100], [500,100], [500,300], [200,300], [200,100]])

obstaculo = Polygon(vertices_1, color=orange,parent = view.scene) #Para mostrar

###################### Dibujamos los rayos de inflección
get_sharp_vertex(vertices_1)
######################


timer = app.Timer()
#timer.connect(update)
timer.start()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()

