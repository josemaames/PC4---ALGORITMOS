"""
MAPAS (OPCIONAL) - generadores de cuadriculas para la interfaz.
Usa numpy y random (NO es parte de los algoritmos de busqueda).
Codigos: 0 = LIBRE (costo 1), 1 = PARED, 2 = BARRO (costo 5)
"""
import random
import numpy as np

LIBRE, PARED, BARRO = 0, 1, 2
MOVIMIENTOS = ((-1, 0), (0, 1), (1, 0), (0, -1))

# --------------------------------------------------------------------------- #
# Generadores de mapas
# --------------------------------------------------------------------------- #
def _despejar_extremos(grid):
    filas, cols = grid.shape
    grid[1, 1] = LIBRE
    grid[filas - 2, cols - 2] = LIBRE
    return grid


def generar_laberinto(filas, cols, semilla=None, lazos=0.06):
    """Laberinto por backtracking iterativo (DFS aleatorio) + algunos 'lazos'
    (paredes derribadas) para que existan varios caminos."""
    rng = random.Random(semilla)
    grid = np.full((filas, cols), PARED, dtype=np.int8)
    grid[1, 1] = LIBRE
    pila = [(1, 1)]
    while pila:
        f, c = pila[-1]
        opciones = []
        for df, dc in MOVIMIENTOS:
            nf, nc = f + 2 * df, c + 2 * dc
            if 1 <= nf < filas - 1 and 1 <= nc < cols - 1 and grid[nf, nc] == PARED:
                opciones.append((nf, nc, f + df, c + dc))
        if opciones:
            nf, nc, pf, pc = rng.choice(opciones)
            grid[pf, pc] = LIBRE
            grid[nf, nc] = LIBRE
            pila.append((nf, nc))
        else:
            pila.pop()
    candidatos = [
        (f, c) for f in range(1, filas - 1) for c in range(1, cols - 1)
        if grid[f, c] == PARED and (
            (grid[f - 1, c] == LIBRE and grid[f + 1, c] == LIBRE)
            or (grid[f, c - 1] == LIBRE and grid[f, c + 1] == LIBRE))
    ]
    rng.shuffle(candidatos)
    for f, c in candidatos[: int(len(candidatos) * lazos)]:
        grid[f, c] = LIBRE
    return _despejar_extremos(grid)


def generar_aleatorio(filas, cols, p_pared=0.22, p_barro=0.12, semilla=None):
    """Mapa con paredes y barro esparcidos al azar (puede no tener solución)."""
    rng = np.random.default_rng(semilla)
    r = rng.random((filas, cols))
    grid = np.full((filas, cols), LIBRE, dtype=np.int8)
    grid[r < p_pared] = PARED
    grid[(r >= p_pared) & (r < p_pared + p_barro)] = BARRO
    return _despejar_extremos(grid)


def generar_terreno(filas, cols, semilla=None):
    """Zonas rectangulares de barro y muros: muestra bien la diferencia entre
    BFS (minimiza pasos) y Dijkstra/A* (minimizan costo)."""
    rng = random.Random(semilla)
    grid = np.full((filas, cols), LIBRE, dtype=np.int8)
    for _ in range(6):
        h, w = rng.randint(3, 7), rng.randint(5, 12)
        f, c = rng.randint(0, filas - h), rng.randint(0, cols - w)
        grid[f:f + h, c:c + w] = BARRO
    for _ in range(5):
        if rng.random() < 0.5:  # muro vertical
            c = rng.randint(4, cols - 5)
            f0 = rng.randint(0, filas // 2)
            largo = rng.randint(filas // 3, filas * 2 // 3)
            grid[f0:f0 + largo, c] = PARED
        else:                   # muro horizontal
            f = rng.randint(3, filas - 4)
            c0 = rng.randint(0, cols // 2)
            largo = rng.randint(cols // 4, cols // 2)
            grid[f, c0:c0 + largo] = PARED
    return _despejar_extremos(grid)
