# Reglas — NEREID, ronda 1

## Objetivo

Cada competidor programa un agente capaz de mover un vehículo autónomo por un mapa submarino, visitar todos los objetivos y regresar a la base usando la menor cantidad posible de energía y evitando movimientos inválidos.

## Código neutral

Durante una ronda se considera código neutral:

- `common/`
- `judge/`
- `tests/`
- `.github/workflows/`

Cualquier cambio en esas rutas debe ser conocido por ambos antes de utilizarse para puntuar una ronda.

## Código de cada competidor

Adri trabaja en:

`players/adri/solution.py`

Raquel trabaja en:

`players/raquel/solution.py`

Cada solución debe exponer:

```python
def decide(observation: dict) -> str:
    ...
```

Acciones permitidas:

- `UP`
- `DOWN`
- `LEFT`
- `RIGHT`
- `WAIT`

## Información disponible

En la ronda 1 el agente conoce:

- su posición;
- la posición de la base;
- los objetivos que quedan;
- los obstáculos;
- el tamaño del mapa;
- la energía restante;
- el número de pasos realizados.

En rondas posteriores se podrá limitar esta información o introducir ruido en los sensores.

## Puntuación por misión

- `+100` por cada objetivo visitado.
- `+200` por regresar a la base después de visitar todos los objetivos.
- `+1` por cada unidad de energía restante si la misión se completa.
- `-2` por cada movimiento inválido contra un límite del mapa u obstáculo.

La puntuación de una ronda es la suma obtenida en todos los escenarios oficiales.

## Escenarios

Los escenarios oficiales se generan con semillas fijas y se ejecutan de forma idéntica para ambos jugadores. No se permite modificar el generador o las semillas durante una ronda ya iniciada.

## Uso de IA

Está permitido utilizar asistentes de programación, modelos generativos, documentación, buscadores, librerías y cualquier otra herramienta legal disponible para ambos.

Si se utiliza una API de pago específicamente para ejecutar la solución durante el benchmark, ambos deben acordar antes un presupuesto o límite equivalente.

## Entrega de una ronda

1. Cada competidor trabaja en su rama.
2. Cuando una solución esté lista, se ejecutan las pruebas y el juez.
3. Se congela el código que va a competir.
4. Se ejecuta el benchmark oficial sobre ambas soluciones.
5. Después de la ronda podéis revisar y explicar las soluciones del otro.

## Principio general

La finalidad es aprender y comparar enfoques. Las reglas pueden evolucionar entre rondas, pero no durante una ronda ya comenzada.
