"""Pruebas de los algoritmos. Ejecutar:  python -m pytest -q"""
import networkx as nx
import numpy as np
import pytest

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import algoritmos_v1 as alg

SEMILLAS = range(40)


def _mapas():
    for s in SEMILLAS:
        yield alg.generar_aleatorio(20, 30, semilla=s)
        yield alg.generar_terreno(20, 30, semilla=s)
        yield alg.generar_laberinto(21, 31, semilla=s)


def _extremos(grid):
    f, c = grid.shape
    return (1, 1), (f - 2, c - 2)


def _costo_networkx(grid, ini, meta):
    """Verificación independiente: Dijkstra de networkx sobre el mismo grafo."""
    G = nx.DiGraph()
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            if grid[r, c] != alg.PARED:
                G.add_node((r, c))
                for v in alg.vecinos(grid, (r, c)):
                    G.add_edge((r, c), v, weight=alg.costo_entrada(grid, v))
    try:
        return nx.dijkstra_path_length(G, ini, meta)
    except nx.NetworkXNoPath:
        return None


def _camino_valido(grid, camino, ini, meta):
    assert camino[0] == ini and camino[-1] == meta
    for a, b in zip(camino, camino[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, "pasos no adyacentes"
        assert grid[b] != alg.PARED, "el camino atraviesa una pared"


def test_dijkstra_y_astar_coinciden_con_networkx():
    resueltos = 0
    for grid in _mapas():
        ini, meta = _extremos(grid)
        esperado = _costo_networkx(grid, ini, meta)
        for nombre in ("Dijkstra", "A*"):
            for h in alg.HEURISTICAS.values():
                r = alg.resolver(nombre, grid, ini, meta, h, repeticiones=1)
                if esperado is None:
                    assert not r.encontrado
                else:
                    assert r.encontrado and r.costo == esperado, (nombre, r.costo, esperado)
                    _camino_valido(grid, r.camino, ini, meta)
                    assert alg.costo_camino(grid, r.camino) == r.costo
        resueltos += esperado is not None
    assert resueltos > 50  # que la prueba no sea trivial


def test_bfs_minimiza_pasos_en_mapa_uniforme():
    for s in SEMILLAS:
        grid = alg.generar_laberinto(21, 31, semilla=s)
        ini, meta = _extremos(grid)
        rb = alg.resolver("BFS", grid, ini, meta, repeticiones=1)
        rd = alg.resolver("Dijkstra", grid, ini, meta, repeticiones=1)
        assert rb.encontrado and rb.costo == rd.costo and rb.longitud == rd.longitud


def test_bfs_puede_no_ser_optimo_con_barro_y_dijkstra_si():
    peor = 0
    for s in SEMILLAS:
        grid = alg.generar_terreno(20, 30, semilla=s)
        ini, meta = _extremos(grid)
        rb = alg.resolver("BFS", grid, ini, meta, repeticiones=1)
        rd = alg.resolver("Dijkstra", grid, ini, meta, repeticiones=1)
        if rd.encontrado:
            assert rb.costo >= rd.costo
            peor += rb.costo > rd.costo
    assert peor > 0, "debería existir al menos un mapa donde BFS paga más"


def test_dfs_devuelve_camino_valido_no_necesariamente_optimo():
    for grid in _mapas():
        ini, meta = _extremos(grid)
        esperado = _costo_networkx(grid, ini, meta)
        r = alg.resolver("DFS", grid, ini, meta, repeticiones=1)
        assert r.encontrado == (esperado is not None)
        if r.encontrado:
            _camino_valido(grid, r.camino, ini, meta)
            assert r.costo >= esperado


def test_sin_solucion():
    grid = np.zeros((10, 10), dtype=np.int8)
    grid[:, 5] = alg.PARED  # muro completo
    for nombre in alg.ALGORITMOS:
        r = alg.resolver(nombre, grid, (1, 1), (8, 8), repeticiones=1)
        assert not r.encontrado and r.camino == [] and r.costo == float("inf")


def test_inicio_igual_a_meta():
    grid = np.zeros((5, 5), dtype=np.int8)
    for nombre in alg.ALGORITMOS:
        r = alg.resolver(nombre, grid, (2, 2), (2, 2), repeticiones=1)
        assert r.encontrado and r.camino == [(2, 2)] and r.costo == 0 and r.longitud == 0


def test_astar_expande_menos_que_dijkstra_en_promedio():
    exp_d = exp_a = 0
    for s in SEMILLAS:
        grid = alg.generar_aleatorio(30, 30, p_pared=0.15, p_barro=0.0, semilla=s)
        ini, meta = _extremos(grid)
        rd = alg.resolver("Dijkstra", grid, ini, meta, repeticiones=1)
        ra = alg.resolver("A*", grid, ini, meta, repeticiones=1)
        if rd.encontrado:
            exp_d += rd.expandidos
            exp_a += ra.expandidos
    assert exp_a < exp_d


def test_eventos_terminan_en_fin_y_no_expanden_dos_veces():
    grid = alg.generar_terreno(20, 30, semilla=3)
    ini, meta = _extremos(grid)
    for nombre in alg.ALGORITMOS:
        ev = alg.eventos(nombre, grid, ini, meta)
        assert ev[-1][0] == "fin"
        expandidos = [d for t, d in ev if t == "expandir"]
        assert len(expandidos) == len(set(expandidos)), "nodo expandido dos veces"
        assert ev[-1][1].expandidos == len(expandidos)
