"""
Algoritmos de búsqueda sobre una cuadrícula con terreno (PC4 - C8277).

Mapa:
    LIBRE (0) -> costo de entrar a la celda = 1
    PARED (1) -> intransitable
    BARRO (2) -> costo de entrar a la celda = 5

Movimientos: 4 direcciones (arriba, derecha, abajo, izquierda).

Cada algoritmo es un *generador*: va emitiendo eventos (tipo, dato) para que la
interfaz pueda animar la búsqueda paso a paso:
    ("frontera", nodo)   -> el nodo entró a la estructura de espera
    ("expandir", nodo)   -> el nodo fue sacado y expandido
    ("fin", Resultado)   -> último evento, con camino y estadísticas
"""
from __future__ import annotations

import heapq
import math
import random
import time
from collections import deque
from dataclasses import dataclass, field

import numpy as np

LIBRE, PARED, BARRO = 0, 1, 2
COSTO_CELDA = {LIBRE: 1, BARRO: 5}
MOVIMIENTOS = ((-1, 0), (0, 1), (1, 0), (0, -1))  # arriba, derecha, abajo, izquierda

Nodo = tuple  # (fila, columna)


# --------------------------------------------------------------------------- #
# Modelo
# --------------------------------------------------------------------------- #
@dataclass
class Resultado:
    algoritmo: str
    encontrado: bool
    camino: list = field(default_factory=list)
    costo: float = float("inf")
    expandidos: int = 0
    generados: int = 0
    tiempo_ms: float = 0.0

    @property
    def longitud(self) -> int:
        """Número de pasos del camino (aristas)."""
        return max(len(self.camino) - 1, 0) if self.encontrado else 0


def costo_entrada(grid: np.ndarray, nodo: Nodo) -> int:
    """Costo de entrar a la celda `nodo`."""
    return COSTO_CELDA[int(grid[nodo])]


def vecinos(grid: np.ndarray, nodo: Nodo):
    """Genera los vecinos transitables (4 direcciones) de `nodo`."""
    f, c = nodo
    filas, cols = grid.shape
    for df, dc in MOVIMIENTOS:
        nf, nc = f + df, c + dc
        if 0 <= nf < filas and 0 <= nc < cols and grid[nf, nc] != PARED:
            yield (nf, nc)


def costo_camino(grid: np.ndarray, camino: list) -> int:
    """Suma de los costos de entrada de todas las celdas del camino salvo la inicial."""
    return sum(costo_entrada(grid, n) for n in camino[1:])


# --------------------------------------------------------------------------- #
# Heurísticas (admisibles y consistentes: el costo mínimo por paso es 1)
# --------------------------------------------------------------------------- #
def h_manhattan(a: Nodo, b: Nodo) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h_euclidiana(a: Nodo, b: Nodo) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def h_cero(a: Nodo, b: Nodo) -> float:
    return 0.0


HEURISTICAS = {"Manhattan": h_manhattan, "Euclidiana": h_euclidiana}


# --------------------------------------------------------------------------- #
# Utilidades internas
# --------------------------------------------------------------------------- #
def _reconstruir(padre: dict, meta: Nodo) -> list:
    camino, n = [], meta
    while n is not None:
        camino.append(n)
        n = padre[n]
    return camino[::-1]


def _resultado(nombre, grid, padre, meta, expandidos, generados) -> Resultado:
    """`meta` es None si la búsqueda terminó sin llegar a la meta."""
    if meta is None:
        return Resultado(nombre, False, [], float("inf"), expandidos, generados)
    camino = _reconstruir(padre, meta)
    return Resultado(nombre, True, camino, costo_camino(grid, camino), expandidos, generados)


# --------------------------------------------------------------------------- #
# Algoritmos
# --------------------------------------------------------------------------- #
def bfs(grid, inicio, meta, heuristica=None):
    """Búsqueda en amplitud: cola FIFO. Óptima en número de pasos, no en costo."""
    padre = {inicio: None}
    cola = deque([inicio])
    generados, expandidos = 1, 0
    yield ("frontera", inicio)
    while cola:
        actual = cola.popleft()
        expandidos += 1
        yield ("expandir", actual)
        if actual == meta:
            yield ("fin", _resultado("BFS", grid, padre, meta, expandidos, generados))
            return
        for v in vecinos(grid, actual):
            if v not in padre:
                padre[v] = actual
                cola.append(v)
                generados += 1
                yield ("frontera", v)
    yield ("fin", _resultado("BFS", grid, padre, None, expandidos, generados))


def dfs(grid, inicio, meta, heuristica=None):
    """Búsqueda en profundidad: pila LIFO. Completa en grafos finitos, no óptima."""
    padre = {}
    pila = [(inicio, None)]
    generados, expandidos = 1, 0
    yield ("frontera", inicio)
    while pila:
        actual, p = pila.pop()
        if actual in padre:  # ya expandido por otra rama
            continue
        padre[actual] = p
        expandidos += 1
        yield ("expandir", actual)
        if actual == meta:
            yield ("fin", _resultado("DFS", grid, padre, meta, expandidos, generados))
            return
        # reversed para que el primer vecino (arriba) sea el primero en explorarse
        for v in reversed(list(vecinos(grid, actual))):
            if v not in padre:
                pila.append((v, actual))
                generados += 1
                yield ("frontera", v)
    yield ("fin", _resultado("DFS", grid, padre, None, expandidos, generados))


def dijkstra(grid, inicio, meta, heuristica=None):
    """Dijkstra: cola de prioridad por costo acumulado g(n). Óptimo con costos >= 0."""
    dist = {inicio: 0}
    padre = {inicio: None}
    hecho = set()
    heap = [(0, 0, inicio)]
    contador = 1  # desempata sin comparar tuplas de nodos
    generados, expandidos = 1, 0
    yield ("frontera", inicio)
    while heap:
        g, _, actual = heapq.heappop(heap)
        if actual in hecho:  # entrada obsoleta (se encontró un camino mejor antes)
            continue
        hecho.add(actual)
        expandidos += 1
        yield ("expandir", actual)
        if actual == meta:
            yield ("fin", _resultado("Dijkstra", grid, padre, meta, expandidos, generados))
            return
        for v in vecinos(grid, actual):
            ng = g + costo_entrada(grid, v)
            if ng < dist.get(v, math.inf):
                dist[v] = ng
                padre[v] = actual
                heapq.heappush(heap, (ng, contador, v))
                contador += 1
                generados += 1
                yield ("frontera", v)
    yield ("fin", _resultado("Dijkstra", grid, padre, None, expandidos, generados))


def a_estrella(grid, inicio, meta, heuristica=h_manhattan):
    """A*: prioridad f(n) = g(n) + h(n). Óptimo si h es admisible (y consistente)."""
    dist = {inicio: 0}
    padre = {inicio: None}
    hecho = set()
    h0 = heuristica(inicio, meta)
    heap = [(h0, h0, 0, inicio)]  # (f, h, contador, nodo): a igual f, prefiere menor h
    contador = 1
    generados, expandidos = 1, 0
    yield ("frontera", inicio)
    while heap:
        _, _, _, actual = heapq.heappop(heap)
        if actual in hecho:
            continue
        hecho.add(actual)
        expandidos += 1
        yield ("expandir", actual)
        if actual == meta:
            yield ("fin", _resultado("A*", grid, padre, meta, expandidos, generados))
            return
        g = dist[actual]
        for v in vecinos(grid, actual):
            ng = g + costo_entrada(grid, v)
            if ng < dist.get(v, math.inf):
                dist[v] = ng
                padre[v] = actual
                h = heuristica(v, meta)
                heapq.heappush(heap, (ng + h, h, contador, v))
                contador += 1
                generados += 1
                yield ("frontera", v)
    yield ("fin", _resultado("A*", grid, padre, None, expandidos, generados))


ALGORITMOS = {"BFS": bfs, "DFS": dfs, "Dijkstra": dijkstra, "A*": a_estrella}


# --------------------------------------------------------------------------- #
# Ejecución y comparación
# --------------------------------------------------------------------------- #
def eventos(nombre, grid, inicio, meta, heuristica=h_manhattan) -> list:
    """Todos los eventos de la búsqueda (para animar)."""
    return list(ALGORITMOS[nombre](grid, inicio, meta, heuristica))


def resolver(nombre, grid, inicio, meta, heuristica=h_manhattan, repeticiones=3) -> Resultado:
    """Ejecuta el algoritmo y mide el tiempo (mínimo de `repeticiones`)."""
    mejor, res = math.inf, None
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        for tipo, dato in ALGORITMOS[nombre](grid, inicio, meta, heuristica):
            if tipo == "fin":
                res = dato
        mejor = min(mejor, time.perf_counter() - t0)
    res.tiempo_ms = mejor * 1000
    return res


def comparar(grid, inicio, meta, heuristica=h_manhattan) -> list:
    return [resolver(n, grid, inicio, meta, heuristica) for n in ALGORITMOS]


def tabla_texto(resultados) -> str:
    filas = [f"{'Algoritmo':<10}{'Costo':>8}{'Pasos':>8}{'Expand.':>9}{'Gener.':>9}{'Tiempo ms':>11}"]
    for r in resultados:
        if r.encontrado:
            filas.append(f"{r.algoritmo:<10}{r.costo:>8}{r.longitud:>8}{r.expandidos:>9}"
                         f"{r.generados:>9}{r.tiempo_ms:>11.3f}")
        else:
            filas.append(f"{r.algoritmo:<10}{'sin solución':>16}{r.expandidos:>9}"
                         f"{r.generados:>9}{r.tiempo_ms:>11.3f}")
    return "\n".join(filas)


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
