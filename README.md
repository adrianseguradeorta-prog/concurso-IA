# Concurso IA — Adri vs. Raquel

Repositorio compartido para una competición de programación e inteligencia artificial entre **Adri** y **Raquel**.

La idea es sencilla: ambos reciben el mismo simulador, las mismas reglas y los mismos escenarios. Cada uno desarrolla su propia solución en una carpeta separada y el juez ejecuta ambas soluciones sobre exactamente las mismas misiones.

## Primer reto: NEREID

NEREID es un pequeño simulador de navegación submarina en una cuadrícula. Un vehículo autónomo parte de una base, debe visitar varios objetivos y regresar antes de agotar su energía.

En esta primera versión hay:

- un mapa de 20 × 20;
- una base;
- tres objetivos por misión;
- obstáculos;
- energía limitada;
- escenarios reproducibles mediante semillas aleatorias;
- una interfaz idéntica para los dos competidores;
- un juez que calcula la puntuación automáticamente.

La versión inicial está hecha deliberadamente sencilla. La intención es añadir después corrientes, sensores ruidosos, comunicaciones imperfectas y otras dificultades sin cambiar las reglas a mitad de una ronda.

## Estructura

```text
concurso-IA/
├── common/                 # Simulador compartido
├── judge/                  # Evaluación y marcador
├── players/
│   ├── adri/               # Solución de Adri
│   └── raquel/             # Solución de Raquel
├── tests/                  # Pruebas del código común
├── .github/workflows/      # Ejecución automática en GitHub
├── RULES.md                # Reglas de la competición
└── requirements.txt
```

## Cómo empezar

Necesitáis Python 3.11 o posterior.

```bash
git clone https://github.com/adrianseguradeorta-prog/concurso-IA.git
cd concurso-IA
python -m pip install -r requirements.txt
python -m judge.run_challenge
```

El juez ejecutará ambos agentes sobre los mismos escenarios y mostrará una clasificación.

También podéis probar un único competidor:

```bash
python -m judge.run_challenge --player adri
python -m judge.run_challenge --player raquel
```

## Dónde programa cada uno

Adri modifica principalmente:

```text
players/adri/solution.py
```

Raquel modifica principalmente:

```text
players/raquel/solution.py
```

El punto de entrada obligatorio de cada solución es:

```python
def decide(observation: dict) -> str:
    ...
```

Las acciones válidas son:

```text
UP
DOWN
LEFT
RIGHT
WAIT
```

El agente no recibe acceso directo al objeto interno del simulador. Solo puede decidir a partir de la observación que recibe.

## Ramas de trabajo

La rama `main` contiene las reglas y el código común aceptado por ambos.

Cada competidor tiene su propia rama de desarrollo:

```text
adri-dev
raquel-dev
```

La recomendación es trabajar normalmente en vuestra rama y llevar los cambios a `main` mediante pull request cuando queráis congelar o compartir una versión.

## Filosofía de la competición

Se puede usar ChatGPT, Copilot u otras herramientas de IA. El objetivo no es competir contra la IA, sino aprender a diseñar una solución mejor utilizando las mismas posibilidades.

El código de `common/`, `judge/` y `tests/` es terreno neutral. Durante una ronda no debe modificarse unilateralmente para favorecer una solución.

Las reglas completas están en [RULES.md](RULES.md).
