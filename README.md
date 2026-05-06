# Agente Reactivo Simple

Simulación visual de un agente reactivo que navega una malla aleatoria usando reglas de percepción. El agente detecta su entorno con 3 sensores frontales y decide si avanzar, girar a la derecha o girar a la izquierda. Al ejecutar el script, primero corre una prueba en consola de 5 pasos y luego abre la simulación visual. La simulación se detiene automáticamente cuando el agente entra en un ciclo, muestra el desempeño en pantalla y guarda un registro completo en CSV.

## Requisitos

- Python 3.8 o superior
- pip

## Instalación de dependencias

```bash
pip install numpy pygame
```

## Ejecución

```bash
python agente_reactivo_simple_2.py
```

## Flujo de ejecución

Al correr el script suceden dos cosas en orden:

1. **Prueba en consola** — imprime el estado inicial de la malla, ejecuta los primeros 5 pasos del agente y muestra el desempeño en la terminal.
2. **Simulación visual** — abre una ventana pygame con un agente nuevo que navega hasta detectar un ciclo.

## Controles

| Acción | Cómo |
|--------|------|
| Cerrar la ventana | Clic en la X |

## Descripción del entorno

La malla se genera aleatoriamente con tres tipos de celda:

| Valor | Color | Significado |
|-------|-------|-------------|
| `0` | Gris oscuro | Celda oscura (línea) |
| `1` | Gris claro | Celda clara (fondo) |
| `2` | Rojo | Pared (borde) |

El agente (triángulo azul) apunta hacia su dirección actual: Norte, Sur, Este u Oeste.

## Comportamiento del agente

El agente percibe las 3 celdas frente a él (izquierda, centro, derecha) y selecciona una acción según una tabla de reglas. Las acciones posibles son `AVANZAR`, `GIRAR_DERECHA` y `GIRAR_IZQUIERDA`.

### Detección de ciclo (watchdog)

El agente guarda un historial de posiciones visitadas `(x, y, orientacion)`. Si vuelve a la misma posición con la misma orientación, la simulación se pausa y muestra en pantalla:

- Mensaje **"CICLO DETECTADO — simulacion detenida"** en rojo.
- Mensaje de **desempeño del agente** en amarillo.

### Desempeño del agente

El agente mantiene tres registros internos:

| Atributo | Contenido |
|----------|-----------|
| `visitados` | Lista de `(x, y, orientacion)` — usado por el watchdog |
| `cvisitados` | Lista de celdas únicas `(x, y)` pisadas — sin repetir |
| `totalinfovisitados` | Lista completa con percepción en cada paso |

Al detenerse calcula y muestra el porcentaje de desempeño basado en las celdas visitadas.

## Registro de movimientos

Al detenerse se genera automáticamente `registro_agente.csv` en la misma carpeta del script:

| Columna | Descripción |
|---------|-------------|
| `Numero` | Número de paso (01, 02, ...) |
| `Posicion` | Coordenada (x, y) antes del movimiento |
| `Orientacion` | Dirección antes del movimiento (N/S/E/O) |
| `f_izq` | Valor del sensor izquierdo |
| `f_cen` | Valor del sensor central |
| `f_der` | Valor del sensor derecho |
| `Regla` | Regla que se aplicó |
| `Accion` | Acción ejecutada |
| `Pos_nueva` | Coordenada (x, y) después del movimiento |
| `Ori_nueva` | Dirección después del movimiento |

## Estructura del proyecto

```
agente_reactivo_simple_2.py   # código principal
registro_agente.csv           # generado al ejecutar (no incluido en el repo)
```

## Dependencias

| Librería | Uso |
|----------|-----|
| `numpy` | Generación y manejo de la malla como matriz |
| `pygame` | Ventana gráfica y dibujado |
| `csv`, `os`, `sys`, `random` | Módulos estándar de Python |
