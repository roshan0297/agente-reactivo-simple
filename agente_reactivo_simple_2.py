import numpy as np   # para crear y manejar la malla como matriz numérica
import random        # para posición inicial y orientación aleatoria del agente
import pygame        # para la ventana y el dibujo
import sys           # para cerrar la ventana correctamente
import csv           # para guardar el registro de movimientos
import os            # para construir la ruta del archivo de registro

# ─────────────────────────────────────────────────────────────────────────────
# CLASE ENTORNO — sin cambios
# ─────────────────────────────────────────────────────────────────────────────

class Entorno:

    def __init__(self, n, m):
        self.n     = n
        self.m     = m
        self.malla = self._generar_malla()

    def _generar_malla(self):
        # 0 = celda OSCURA (línea)
        # 1 = celda CLARA  (fondo)
        # 2 = PARED        (borde)
        opciones       = [0, 1]
        probabilidades = [0.3, 0.7]   # 20% oscuro, 90% claro

        malla_generada = np.random.choice(
            opciones, size=(self.n, self.m), p=probabilidades
        )

        # Rodear con capa de paredes (2)
        malla_pared             = np.full((self.n + 2, self.m + 2), 2)
        malla_pared[1:-1, 1:-1] = malla_generada

        return malla_pared

    def mostrar(self):
        print(self.malla)   # debug en consola si se necesita


# ─────────────────────────────────────────────────────────────────────────────
# CLASE AGENTE REACTIVO — sin cambios
# ─────────────────────────────────────────────────────────────────────────────

class AgenteReactivo:

    def __init__(self, entorno):
        self.entorno          = entorno
        self.y                = random.randint(1, entorno.n)
        self.x                = random.randint(1, entorno.m)
        self.brujula          = ['N', 'E', 'S', 'O']
        self.orientacion      = random.choice(self.brujula)
        self.visitados        = []   # (x, y, orientacion)
        self.cvisitados       = []   # (x, y) sin repetir
        self.totalinfovisitados = [] # (x, y, orientacion, actual, f_izq, f_cen, f_der)
        self.registrar_posicion()

    # Sirve para guardar la posicion y orientación del robot
    def registrar_posicion(self):
        percepcion = self.percibir()
        posicion   = (self.x, self.y, self.orientacion)
        cuadro     = (self.x, self.y)
        total      = (self.x, self.y, self.orientacion,
                      percepcion[0], percepcion[1], percepcion[2], percepcion[3])
        self.visitados.append(posicion)
        if cuadro not in self.cvisitados:
            self.cvisitados.append(cuadro)
        self.totalinfovisitados.append(total)

    # Sirve para verificar si la nueva posicion ya ha sido visitada con la misma orientación
    def watch_dog(self):
        nueva_posicion = (self.x, self.y, self.orientacion)
        return nueva_posicion in self.visitados

    # Sirve para comparar los cuadros visitados entre el total de cuadros
    def desempeno_agente(self):
        porcentaje = sum(fila.count(0) for fila in self.cvisitados) * 100 / len(self.cvisitados)
        mensaje = f"El desempeno del agente fue: {porcentaje:.1f}%"
        print(mensaje)
        return mensaje

    def percibir(self):
        # Offsets de las 3 cámaras frontales según orientación
        offsets = {
            'N': {'f_izq': (-1, -1), 'f_cen': (-1,  0), 'f_der': (-1,  1)},
            'S': {'f_izq': ( 1,  1), 'f_cen': ( 1,  0), 'f_der': ( 1, -1)},
            'E': {'f_izq': (-1,  1), 'f_cen': ( 0,  1), 'f_der': ( 1,  1)},
            'O': {'f_izq': ( 1, -1), 'f_cen': ( 0, -1), 'f_der': (-1, -1)},
        }
        mi_offset = offsets[self.orientacion]

        actual = self.entorno.malla[self.y, self.x]
        f_izq  = self.entorno.malla[self.y + mi_offset['f_izq'][0],
                                     self.x + mi_offset['f_izq'][1]]
        f_cen  = self.entorno.malla[self.y + mi_offset['f_cen'][0],
                                     self.x + mi_offset['f_cen'][1]]
        f_der  = self.entorno.malla[self.y + mi_offset['f_der'][0],
                                     self.x + mi_offset['f_der'][1]]

        return [actual, f_izq, f_cen, f_der]

    # Tabla de reglas: (actual, f_izq, f_cen, f_der) -> accion
            # Tabla de reglas: (actual, f_izq, f_cen, f_der) -> accion
    _REGLAS = {
       # actual=1, f_izq=1 (Escenarios Luis Muñoz)
        (1, 1, 1, 2): "GIRAR_IZQUIERDA",
        (1, 1, 1, 1): "GIRAR_IZQUIERDA",
        (1, 1, 1, 0): "GIRAR_DERECHA",
        (1, 1, 0, 2): "GIRAR_IZQUIERDA",
        (1, 1, 0, 1): "AVANZAR",
        (1, 1, 0, 0): "AVANZAR",
        # actual=1, f_izq=0 (Parte Derly)
        (1, 0, 1, 1): "GIRAR_IZQUIERDA",
        (1, 0, 1, 0): "GIRAR_IZQUIERDA",
        (1, 0, 1, 2): "GIRAR_IZQUIERDA",
        (1, 0, 0, 1): "AVANZAR",
        (1, 0, 0, 2): "AVANZAR",
        (1, 0, 0, 0): "AVANZAR",
        # actual=1, f_izq=2

        (1, 2, 1, 0): "GIRAR_DERECHA",
        (1, 2, 1, 1): "AVANZAR",
        (1, 2, 1, 2): "AVANZAR",
        (1, 2, 0, 0): "AVANZAR",
        (1, 2, 0, 1): "AVANZAR",
        (1, 2, 0, 2): "AVANZAR",

        (0, 1, 1, 1): "GIRAR_DERECHA",
        (0, 1, 1, 0): "GIRAR_DERECHA",
        (0, 1, 1, 2): "AVANZAR",
        (0, 1, 0, 1): "AVANZAR",
        (0, 1, 0, 0): "AVANZAR",
        (0, 1, 0, 2): "AVANZAR",

        (0, 0, 1, 1): "AVANZAR",
        (0, 0, 1, 0): "GIRAR_DERECHA",
        (0, 0, 1, 2): "AVANZAR",
        (0, 0, 0, 1): "AVANZAR",
        (0, 0, 0, 0): "AVANZAR",
        (0, 0, 0, 2): "AVANZAR",
        # actual=0
        (0, 2, 1, 1): "GIRAR_DERECHA",
        (0, 2, 1, 0): "GIRAR_DERECHA",
        (0, 2, 1, 2): "AVANZAR",
        (0, 2, 0, 1): "AVANZAR",
        (0, 2, 0, 0): "AVANZAR",
        (0, 2, 0, 2): "AVANZAR",

        (0,2,2,2): "GIRAR_DERECHA",#pared en las tres camaras cuadro negro
        (1,2,2,2): "GIRAR_DERECHA",#pared en las tres camaras cuadro blanco

    }
    def decidir_accion(self, percepcion):
        actual, f_izq, f_cen, f_der = percepcion

        if f_cen == 2:
            return "GIRAR_IZQUIERDA", "f_cen=PARED"

        clave = (actual, f_izq, f_cen, f_der)
        if clave in self._REGLAS:
            return self._REGLAS[clave], str(clave)
        return "AVANZAR", "default"

    def ejecutar_accion(self, accion):
        if accion == "GIRAR_DERECHA":
            idx = self.brujula.index(self.orientacion)
            self.orientacion = self.brujula[(idx + 1) % 4]   # N→E→S→O→N

        elif accion == "GIRAR_IZQUIERDA":
            idx = self.brujula.index(self.orientacion)
            self.orientacion = self.brujula[(idx - 1) % 4]   # N→O→S→E→N

        elif accion == "AVANZAR":
            if   self.orientacion == 'N': self.y -= 1
            elif self.orientacion == 'S': self.y += 1
            elif self.orientacion == 'E': self.x += 1
            elif self.orientacion == 'O': self.x -= 1


# ─────────────────────────────────────────────────────────────────────────────
# GUARDADO DE REGISTRO
# ─────────────────────────────────────────────────────────────────────────────

_RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'registro_agente.csv')

def guardar_registro(registro):
    with open(_RUTA_CSV, 'w', newline='', encoding='utf-8') as f:
        campos = ['Numero', 'Posicion', 'Orientacion', 'f_izq', 'f_cen', 'f_der',
                  'Regla', 'Accion', 'Pos_nueva', 'Ori_nueva']
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registro)


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────

N         = 15
M         = 15
TAM       = 36
VELOCIDAD = 10

OSCURO = (40,  40,  40)
CLARO  = (210, 210, 210)
PARED  = (160, 50,  50)
AGENTE = (50,  120, 255)

# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Prueba en consola (primeros 5 pasos) ──────────────────────────────────
    mi_entorno = Entorno(N, M)
    mi_agente  = AgenteReactivo(mi_entorno)

    print("--- ESTADO INICIAL ---")
    mi_entorno.mostrar()

    for paso in range(1, 6):
        if len(mi_agente.cvisitados) == M * N:
            print(f"Se visitaron todas las posiciones del entorno: {len(mi_agente.cvisitados)}")
            break
        percepcion  = mi_agente.percibir()
        accion, _   = mi_agente.decidir_accion(percepcion)   # FIX 1: desempacar tupla
        print(f"\n--- PASO {paso} ---")
        print(f"Posicion: ({mi_agente.x}, {mi_agente.y})  Orientacion: {mi_agente.orientacion}")
        print(f"Percibe: {percepcion}")
        print(f"Decide: {accion}")
        mi_agente.ejecutar_accion(accion)
        if mi_agente.watch_dog():
            break
        else:
            mi_agente.registrar_posicion()

    mi_agente.desempeno_agente()

    # ── Simulación visual con pygame ──────────────────────────────────────────
    mi_entorno = Entorno(N, M)
    mi_agente  = AgenteReactivo(mi_entorno)

    pygame.init()

    filas  = mi_entorno.malla.shape[0]
    cols   = mi_entorno.malla.shape[1]
    ANCHO  = cols  * TAM
    ALTO   = filas * TAM + 40

    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Agente Reactivo Simple")

    fuente = pygame.font.SysFont("monospace", 14)
    reloj  = pygame.time.Clock()

    paso          = 0
    accion        = "-"
    detenido      = False
    registro      = []
    msg_desempeno = ""

    while True:

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not detenido:
            percepcion                    = mi_agente.percibir()
            actual, f_izq, f_cen, f_der   = percepcion
            pos_antes                     = (mi_agente.x, mi_agente.y)
            ori_antes                     = mi_agente.orientacion

            accion, regla = mi_agente.decidir_accion(percepcion)
            mi_agente.ejecutar_accion(accion)
            paso += 1

            registro.append({
                'Numero'     : f"{paso:02d}",
                'Posicion'   : f"({pos_antes[0]},{pos_antes[1]})",
                'Orientacion': ori_antes,
                'f_izq'      : f_izq,
                'f_cen'      : f_cen,
                'f_der'      : f_der,
                'Regla'      : regla,
                'Accion'     : accion,
                'Pos_nueva'  : f"({mi_agente.x},{mi_agente.y})",
                'Ori_nueva'  : mi_agente.orientacion,
            })

            if mi_agente.watch_dog():
                detenido      = True
                msg_desempeno = mi_agente.desempeno_agente()
                guardar_registro(registro)
            else:
                mi_agente.registrar_posicion()

        ventana.fill((20, 20, 20))

        for fila in range(filas):
            for col in range(cols):
                valor = mi_entorno.malla[fila, col]
                if   valor == 0: color = OSCURO
                elif valor == 1: color = CLARO
                else:            color = PARED
                pygame.draw.rect(ventana, color, (col * TAM, fila * TAM, TAM - 1, TAM - 1))

        cx = mi_agente.x * TAM + TAM // 2
        cy = mi_agente.y * TAM + TAM // 2
        r  = TAM // 2 - 4
        puntos = {
            'N': [(cx, cy-r), (cx-r, cy+r), (cx+r, cy+r)],
            'S': [(cx, cy+r), (cx-r, cy-r), (cx+r, cy-r)],
            'E': [(cx+r, cy), (cx-r, cy-r), (cx-r, cy+r)],
            'O': [(cx-r, cy), (cx+r, cy-r), (cx+r, cy+r)],
        }
        pygame.draw.polygon(ventana, AGENTE, puntos[mi_agente.orientacion])

        info  = f"Paso: {paso}  |  Accion: {accion}  |  Pos: ({mi_agente.x},{mi_agente.y})  |  Dir: {mi_agente.orientacion}"
        texto = fuente.render(info, True, (255, 255, 255))
        ventana.blit(texto, (8, ALTO - 30))

        if detenido:
            aviso    = fuente.render("CICLO DETECTADO — simulacion detenida", True, (255, 80, 80))
            desmp    = fuente.render(msg_desempeno, True, (255, 220, 50))
            centro_y = ALTO // 2 - aviso.get_height()
            ventana.blit(aviso, (ANCHO // 2 - aviso.get_width() // 2, centro_y))
            ventana.blit(desmp, (ANCHO // 2 - desmp.get_width() // 2, centro_y + aviso.get_height() + 6))

        pygame.display.flip()
        reloj.tick(VELOCIDAD)
