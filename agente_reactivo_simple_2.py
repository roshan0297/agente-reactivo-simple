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
        self.visitados        = []
        self.cvisitados       = []
        self.totalinfovisitados = []
        self.registrar_posicion()

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

    def watch_dog(self):
        return (self.x, self.y, self.orientacion) in self.visitados

    def desempeno_agente(self):
        total_celdas = self.entorno.n * self.entorno.m
        porcentaje   = len(self.cvisitados) * 100 / total_celdas
        mensaje = f"Desempeno: {porcentaje:.1f}% ({len(self.cvisitados)}/{total_celdas} celdas)"
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
        # 0 = celda OSCURA (línea)
        # 1 = celda CLARA  (fondo)
        # 2 = PARED        (borde)
        (1, 1, 1, 2): "GIRAR_IZQUIERDA",#(▢,▢,▢,▢,­­▧)
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
# PROGRAMA PRINCIPAL CON PYGAME
# ─────────────────────────────────────────────────────────────────────────────

# ── Configuración ─────────────────────────────────────────────────────────────
N         = 15    # filas del tablero interior
M         = 15    # columnas del tablero interior
TAM       = 36    # tamaño de cada celda en píxeles
VELOCIDAD = 10     # pasos por segundo

# ── Colores RGB ───────────────────────────────────────────────────────────────
OSCURO = (40,  40,  40)    # celda 0 → gris oscuro
CLARO  = (210, 210, 210)   # celda 1 → gris claro
PARED  = (160, 50,  50)    # celda 2 → rojo
AGENTE = (50,  120, 255)   # triángulo del agente → azul

# ── Crear entorno y agente ────────────────────────────────────────────────────
mi_entorno = Entorno(N, M)
mi_agente  = AgenteReactivo(mi_entorno)

# ── Iniciar pygame ────────────────────────────────────────────────────────────
pygame.init()

filas  = mi_entorno.malla.shape[0]   # N + 2 (con paredes)
cols   = mi_entorno.malla.shape[1]   # M + 2
ANCHO  = cols  * TAM
ALTO   = filas * TAM + 40            # +40px para texto inferior

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Agente Reactivo Simple")

fuente = pygame.font.SysFont("monospace", 14)
reloj  = pygame.time.Clock()

paso          = 0
accion        = "-"
detenido      = False
registro      = []
msg_desempeno = ""

# ── Bucle principal ───────────────────────────────────────────────────────────
while True:

    # 1. Cerrar ventana con la X
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Un paso del agente: percibir → decidir → ejecutar (solo si no está detenido)
    if not detenido:
        percepcion           = mi_agente.percibir()
        actual, f_izq, f_cen, f_der = percepcion
        pos_antes            = (mi_agente.x, mi_agente.y)
        ori_antes            = mi_agente.orientacion

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

    # 3. Dibujar el tablero celda por celda
    ventana.fill((20, 20, 20))

    for fila in range(filas):
        for col in range(cols):
            valor = mi_entorno.malla[fila, col]

            if   valor == 0: color = OSCURO
            elif valor == 1: color = CLARO
            else:            color = PARED

            # Dibujar rectángulo con separación de 1px entre celdas
            pygame.draw.rect(
                ventana, color,
                (col * TAM, fila * TAM, TAM - 1, TAM - 1)
            )

    # 4. Dibujar agente como triángulo apuntando en su dirección
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

    # 5. Texto informativo en la franja inferior
    info  = f"Paso: {paso}  |  Accion: {accion}  |  Pos: ({mi_agente.x},{mi_agente.y})  |  Dir: {mi_agente.orientacion}"
    texto = fuente.render(info, True, (255, 255, 255))
    ventana.blit(texto, (8, ALTO - 30))

    if detenido:
        fuente_grande = pygame.font.SysFont("monospace", 20, bold=True)
        txt_titulo = fuente_grande.render("CICLO DETECTADO",     True, (255, 80,  80))
        txt_sub    = fuente_grande.render("Simulacion detenida", True, (255, 255, 255))
        txt_desemp = fuente_grande.render(msg_desempeno,         True, (255, 220,  50))

        pad       = 24
        ancho_caja = max(txt_titulo.get_width(), txt_sub.get_width(), txt_desemp.get_width()) + pad * 2
        alto_caja  = txt_titulo.get_height() + txt_sub.get_height() + txt_desemp.get_height() + pad * 3 + 16
        cx_caja    = (ANCHO - ancho_caja) // 2
        cy_caja    = (ALTO  - alto_caja)  // 2

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        ventana.blit(overlay, (0, 0))

        pygame.draw.rect(ventana, (30, 30, 30),  (cx_caja, cy_caja, ancho_caja, alto_caja), border_radius=12)
        pygame.draw.rect(ventana, (255, 80, 80), (cx_caja, cy_caja, ancho_caja, alto_caja), width=3, border_radius=12)

        y = cy_caja + pad
        for superficie in [txt_titulo, txt_sub, txt_desemp]:
            ventana.blit(superficie, (cx_caja + (ancho_caja - superficie.get_width()) // 2, y))
            y += superficie.get_height() + 8

    # 6. Actualizar pantalla y controlar velocidad
    pygame.display.flip()
    reloj.tick(VELOCIDAD)
