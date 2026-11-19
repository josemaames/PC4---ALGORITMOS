"""
PRUEBAS SIMPLES (solo assert, SIN pytest):  python test_clase.py
Se compara el nucleo del profesor contra la version v1 (opcional/) y se
verifica que las rutas sean validas.
"""
import sys
sys.path.insert(0, "opcional")
import busqueda_clase as bc
import mapas
import algoritmos_v1 as v1   # version v1 (generadores), solo para comparar


def mapas_de_prueba():
    for s in range(15):
        yield mapas.generar_aleatorio(20, 30, semilla=s)
        yield mapas.generar_terreno(20, 30, semilla=s)
        yield mapas.generar_laberinto(21, 31, semilla=s)


def ruta_valida(grid, camino, ini, meta):
    assert camino[0] == ini and camino[-1] == meta
    for a, b in zip(camino, camino[1:]):
        assert abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1
        assert grid[b[0]][b[1]] != bc.PARED


def main():
    n = 0
    for grid in mapas_de_prueba():
        ini, meta = (1, 1), (len(grid)-2, len(grid[0])-2)
        ref = v1.resolver("Dijkstra", grid, ini, meta, repeticiones=1)
        for nombre in bc.ALGORITMOS:
            for h in bc.HEURISTICAS.values():
                r = bc.resolver(nombre, grid, ini, meta, h, repeticiones=1)
                assert r.encontrado == ref.encontrado, (nombre, "existencia")
                if not r.encontrado:
                    continue
                ruta_valida(grid, r.camino, ini, meta)
                assert bc.costo_camino(grid, r.camino) == r.costo
                if nombre in ("Dijkstra", "A*"):
                    assert r.costo == ref.costo, (nombre, r.costo, ref.costo)
                else:
                    assert r.costo >= ref.costo
        n += 1
    print(f"OK: {n} mapas, 5 algoritmos x 2 heuristicas")


    # BFS = DIJKSTRA EN LABERINTOS (COSTOS UNIFORMES)
    for sem in range(15):
        g = mapas.generar_laberinto(21, 31, semilla=sem)
        ini, meta = (1, 1), (19, 29)
        rb = bc.resolver("BFS", g, ini, meta, repeticiones=1)
        rd = bc.resolver("Dijkstra", g, ini, meta, repeticiones=1)
        assert rb.costo == rd.costo and rb.longitud == rd.longitud
    # CON BARRO: BFS NUNCA PAGA MENOS Y AL MENOS UNA VEZ PAGA MAS
    mas = 0
    for sem in range(15):
        g = mapas.generar_terreno(20, 30, semilla=sem)
        ini, meta = (1, 1), (18, 28)
        rb = bc.resolver("BFS", g, ini, meta, repeticiones=1)
        rd = bc.resolver("Dijkstra", g, ini, meta, repeticiones=1)
        assert rb.costo >= rd.costo
        mas += rb.costo > rd.costo
    assert mas >= 1
    # NINGUN NODO SE EXPANDE DOS VECES Y LA LISTA TERMINA EN "fin"
    g = mapas.generar_terreno(20, 30, semilla=3)
    for nombre in bc.ALGORITMOS:
        ev = bc.eventos(nombre, g, (1, 1), (18, 28))
        exp = [n for t, n in ev if t == "expandir"]
        assert len(exp) == len(set(exp)) and ev[-1][0] == "fin"
    # A* EXPANDE MENOS QUE DIJKSTRA EN PROMEDIO (MAPAS SIN BARRO)
    ea = ed = 0
    for sem in range(15):
        g = mapas.generar_aleatorio(30, 30, p_pared=0.15, p_barro=0.0, semilla=sem)
        ra = bc.resolver("A*", g, (1, 1), (28, 28), repeticiones=1)
        rd = bc.resolver("Dijkstra", g, (1, 1), (28, 28), repeticiones=1)
        if rd.encontrado:
            ea += ra.expandidos; ed += rd.expandidos
    assert ea < ed
    print("OK: BFS vs Dijkstra, sin repetidos, A* vs Dijkstra")

    # SIN SOLUCION
    grid = [[0]*10 for _ in range(10)]
    for r in range(10):
        grid[r][5] = 1
    for nombre in bc.ALGORITMOS:
        assert not bc.resolver(nombre, grid, (1, 1), (8, 8), repeticiones=1).encontrado
    # INICIO == META
    for nombre in bc.ALGORITMOS:
        r = bc.resolver(nombre, [[0]*5 for _ in range(5)], (2, 2), (2, 2), repeticiones=1)
        assert r.encontrado and r.costo == 0
    # ESTRUCTURAS DEL PROFESOR
    from estructuras_clase import myQueue, myStack, MinHeap
    q = myQueue(3); q.enqueue(1); q.enqueue(2); q.enqueue(3)
    assert q.dequeue() == 1 and q.getFront() == 2 and q.getRear() == 3
    s = myStack(3); s.push(1); s.push(2)
    assert s.pop() == 2 and s.peek() == 1
    h = MinHeap()
    for x in (5, 3, 8, 1, 9):
        h.insert(x)
    assert [h.extract_min() for _ in range(5)] == [1, 3, 5, 8, 9]
    print("OK: casos borde y estructuras (myQueue, myStack, MinHeap)")


if __name__ == "__main__":
    main()
