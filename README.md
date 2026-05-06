# Agente Reactivo Simple

Simulación visual de un agente reactivo que navega una malla aleatoria usando reglas de percepción. El agente detecta su entorno con 3 sensores frontales y decide si avanzar, girar a la derecha o girar a la izquierda. La simulación se detiene automáticamente cuando el agente entra en un ciclo, y guarda un registro completo de cada movimiento en un archivo CSV.

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

El agente percibe las 3 celdas frente a él (izquierda, centro, derecha) y selecciona una acción según una tabla de reglas. Si detecta que volvió a una posición ya visitada con la misma orientación (**watchdog**), la simulación se pausa y queda la pantalla estática con el mensaje **"CICLO DETECTADO"**.

## Registro de movimientos

Al detenerse, se genera automáticamente el archivo `registro_agente.csv` en la misma carpeta del script con la siguiente estructura:

| Columna | Descripción |
|---------|-------------|
| `Numero` | Número de paso (01, 02, ...) |
| `Posicion` | Coordenada (x, y) antes del movimiento |
| `Orientacion` | Dirección antes del movimiento (N/S/E/O) |
| `f_izq` | Valor del sensor izquierdo |
| `f_cen` | Valor del sensor central |
| `f_der` | Valor del sensor derecho |
| `Regla` | Regla que se aplicó |
| `Accion` | Acción ejecutada (AVANZAR / GIRAR_DERECHA / GIRAR_IZQUIERDA) |
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
