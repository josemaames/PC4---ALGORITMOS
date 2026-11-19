"""
PC4 - C8277 ALGORITMOS Y ESTRUCTURAS DE DATOS
METODOS DE BUSQUEDA: BFS, DFS, DIJKSTRA (COSTO UNIFORME), A* Y VORAZ

ESTE ARCHIVO USA EL MISMO CODIGO Y ESTILO DE LOS LABORATORIOS DEL PROFESOR:
  * BFS  -> LAB 11: Node, GridProblem, breadth_first_search, deque, reached
  * DFS  -> LAB 09: myStack (pila LIFO) + esquema de bfs(graph) con visited
  * DIJKSTRA -> LAB 12: minimo_costo(graph, start, goal) con GG, parent,
                visited, pq (heapq) y la busqueda lineal FLAG/val
  * A*   -> LAB 13: astar(graph, H, start, goal) con pq=(f,g,nodo) y tabla H
  * VORAZ (GREEDY BEST-FIRST) -> SLIDES "Busqueda informada": f(n) = h(n)

MAPA (grid = lista de listas, como en el LAB 11):
  0 = LIBRE (costo 1)   1 = PARED (obstaculo)   2 = BARRO (costo 5)

Para Dijkstra, A* y Voraz el mapa se convierte en un GRAFO como el de las
ciudades de Rumania del profesor: lista de adyacencia con diccionarios
  graph[(fila,col)] = { (vecino): costo_de_entrar_al_vecino, ... }

Cada algoritmo recibe ademas una lista opcional `eventos`. Solo se usa para
que la interfaz pueda ANIMAR la busqueda (agrega ("frontera",n) al meter un
nodo a la estructura y ("expandir",n) al sacarlo). Si es None, no hace nada.
"""
import time
from collections import deque
import heapq
import math

from estructuras_clase import myStack

LIBRE, PARED, BARRO = 0, 1, 2
COSTO_CELDA = {LIBRE: 1, BARRO: 5}

# MOVIMIENTOS (arriba, abajo, izquierda, derecha) - IGUAL QUE EL LAB 11
MOVIMIENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ===============================================================
# 1. BFS  (LAB 11)  -  Node, GridProblem, breadth_first_search
# ===============================================================
class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action


class GridProblem:
    def __init__(self, initial_state, goal_state, grid):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.grid = grid

    def is_goal(self, state):
        return state == self.goal_state

    def is_valid_cell(self, row, col):
        # CHEQUEAMOS SI ESTAMOS DENTRO DEL GRID
        # Y SI NO ES UNA PARED (en el lab: == 0; aqui tambien hay barro)
        return 0 <= row < len(self.grid) and \
               0 <= col < len(self.grid[0]) and \
               self.grid[row][col] != PARED

    def expand(self, node):
        # HALLAMOS EL ESTADO DEL NODO
        row, col = node.state
        # GENERAMOS LOS NODOS HIJOS
        children = []
        for dr, dc in MOVIMIENTOS:
            new_row = row + dr
            new_col = col + dc
            if self.is_valid_cell(new_row, new_col):
                child_state = (new_row, new_col)
                child_node = Node(child_state, parent=node)
                children.append(child_node)
        return children


def breadth_first_search(problem, eventos=None):
    node = Node(problem.initial_state)
    if problem.is_goal(node.state):
        return node
    # FRONTERA = COLA FIFO (deque)
    frontier = deque([node])
    reached = {problem.initial_state}
    if eventos is not None:
        eventos.append(("frontera", node.state))
    while frontier:
        node = frontier.popleft()                  # FIFO
        if eventos is not None:
            eventos.append(("expandir", node.state))
        for child in problem.expand(node):
            state = child.state
            # (COMO EN bfs(graph) DEL LAB 11: SE MARCA AL INSERTAR)
            if state not in reached:
                reached.add(state)
                if problem.is_goal(state):
                    if eventos is not None:
                        eventos.append(("frontera", state))
                    return child
                frontier.append(child)
                if eventos is not None:
                    eventos.append(("frontera", state))
    return None


# FUNCIONES AUXILIARES (LAB 11)
def reconstruct_path(node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))


def print_complete_path(path):
    if path:
        for step, point in enumerate(path):
            print(f"Step {step}: {point}")
    else:
        print("No hay solucion")


# ===============================================================
# 2. GRAFO (lista de adyacencia con diccionarios, LAB 12)
# ===============================================================
def grid_a_grafo(grid):
    """graph[(r,c)] = {(r2,c2): costo de ENTRAR a (r2,c2)}"""
    problem = GridProblem(None, None, grid)
    graph = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == PARED:
                continue
            vecinos = {}
            for dr, dc in MOVIMIENTOS:
                nr, nc = r + dr, c + dc
                if problem.is_valid_cell(nr, nc):
                    vecinos[(nr, nc)] = COSTO_CELDA[int(grid[nr][nc])]
            graph[(r, c)] = vecinos
    return graph


# ===============================================================
# 3. DFS  (LAB 09: myStack  +  esquema de bfs(graph) del LAB 11)
# ===============================================================
def dfs(graph, start, goal, eventos=None):
    # TEST DE META
    if start == goal:
        return {}
    # PILA LIFO (la del lab 09). Capacidad: cada nodo puede entrar
    # hasta una vez por cada arista que llega a el.
    cap = sum(len(v) for v in graph.values()) + 2
    stack = myStack(cap)
    stack.push((start, None))              # (estado, padre)
    visited = set()
    parent = {}
    if eventos is not None:
        eventos.append(("frontera", start))
    # BUSQUEDA
    while not stack.isEmpty():
        node, padre = stack.pop()          # LIFO
        if node in visited:
            continue
        visited.add(node)
        parent[node] = padre
        if eventos is not None:
            eventos.append(("expandir", node))
        # TEST DE META
        if node == goal:
            return parent
        for child in graph[node]:
            if child not in visited:
                stack.push((child, node))
                if eventos is not None:
                    eventos.append(("frontera", child))
    return None                            # NO HAY SOLUCION


# ===============================================================
# 4. DIJKSTRA / COSTO UNIFORME  (LAB 12: minimo_costo)
# ===============================================================
def minimo_costo(graph, start, goal, eventos=None):
    # TEST DE META
    if start == goal:
        return {}, {start: 0}
    # DICCIONARIO PARA GUARDAR COSTO
    GG = {vertex: float('infinity') for vertex in graph}
    GG[start] = 0
    # INICIALIZAMOS LA COLA DE DATOS
    pq = [(0, start)]                      # Nodo inicial
    heapq.heapify(pq)
    visited = set()
    visited.add(start)
    if eventos is not None:
        eventos.append(("frontera", start))
    # BUSQUEDA
    parent = {}                            # La secuencia de busqueda
    while True:
        # SI LA FRONTERA ESTA VACIA
        if len(pq) == 0:
            return [], GG                  # Falla, no solucion
        # SELECCIONAMOS NODO
        g, node = heapq.heappop(pq)
        visited.add(node)
        GG[node] = g
        if eventos is not None:
            eventos.append(("expandir", node))
        # TEST DE META
        if node == goal:
            return parent, GG              # EXITO
        # GENERAMOS NODOS HIJOS
        for child, c in graph[node].items():
            g2 = g + c
            # VERIFICAMOS SI EL ESTADO YA ESTA EN LA FRONTERA
            STATE = child
            N = len(pq)
            val = -1
            FLAG = 0
            for i in range(N):
                if pq[i][1] == STATE:
                    val = pq[i][0]
                    FLAG = 1
                    break
            if child not in visited and FLAG == 0:
                heapq.heappush(pq, (g2, child))
                parent[child] = node
                if eventos is not None:
                    eventos.append(("frontera", child))
            elif FLAG == 1:
                if val > g2:
                    # CAMBIAR EL VALOR DE UN NODO
                    bad_node = (val, child)
                    try:
                        # Buscamos la posicion
                        idx = pq.index(bad_node)
                        # Cambiamos valor
                        pq[idx] = (g2, child)
                        heapq.heapify(pq)
                        # CORRECCION: AL ENCONTRAR UN CAMINO MAS BARATO
                        # HAY QUE ACTUALIZAR TAMBIEN EL PADRE
                        parent[child] = node
                    except ValueError:
                        pass               # Item not found


# ===============================================================
# 5. A*  (LAB 13: astar)   y   VORAZ (f = h)
# ===============================================================
def astar(graph, H, start, goal, eventos=None, voraz=False):
    # NODO INICIAL
    start_node = start
    g = 0
    h = H[start]
    f = g + h
    # DICCIONARIO PARA GUARDAR COSTO
    GG = {vertex: float('infinity') for vertex in graph}
    GG[start] = g
    # TEST DE META
    if start == goal:
        return {}, GG
    # INICIALIZAMOS LA COLA DE PRIORIDAD
    pq = [(f, g, start_node)]              # Nodo inicial
    heapq.heapify(pq)
    visited = set()
    visited.add(start_node)
    if eventos is not None:
        eventos.append(("frontera", start))
    # BUSQUEDA
    parent = {}                            # La secuencia de busqueda
    while True:
        # SI LA FRONTERA ESTA VACIA
        if len(pq) == 0:
            return [], GG                  # Falla, no solucion
        # SELECCIONAMOS NODO
        _, g, node = heapq.heappop(pq)     # Menor f
        visited.add(node)
        GG[node] = g
        if eventos is not None:
            eventos.append(("expandir", node))
        # TEST DE META
        if node == goal:
            return parent, GG              # EXITO
        # GENERAMOS NODOS HIJOS
        for child, c in graph[node].items():
            g2 = g + c
            h2 = H[child]
            # A*: f = g + h      VORAZ: f = h
            f2 = h2 if voraz else g2 + h2
            # VERIFICAMOS SI EL NODO ESTA EN LA COLA DE PRIORIDAD
            STATE = child
            N = len(pq)
            val_f = -1
            val_g = -1
            FLAG = 0
            for i in range(N):
                if pq[i][2] == STATE:
                    val_f = pq[i][0]       # f-value
                    val_g = pq[i][1]       # g-value
                    FLAG = 1
                    break
            if child not in visited and FLAG == 0:
                heapq.heappush(pq, (f2, g2, child))
                parent[child] = node
                if eventos is not None:
                    eventos.append(("frontera", child))
            elif FLAG == 1:
                if val_f > f2:
                    # CAMBIAR EL VALOR DE UN NODO
                    bad_node = (val_f, val_g, child)
                    try:
                        idx = pq.index(bad_node)
                        pq[idx] = (f2, g2, child)
                        heapq.heapify(pq)
                        parent[child] = node   # CORRECCION: ACTUALIZAR PADRE
                    except ValueError:
                        pass


# ===============================================================
# 6. HEURISTICAS (SLIDES "Busqueda informada", seccion 4.4)
# ===============================================================
def h_manhattan(a, b):
    # h(n) = |x_n - x_goal| + |y_n - y_goal|
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def h_euclidiana(a, b):
    # h(n) = sqrt( (x_n - x_goal)^2 + (y_n - y_goal)^2 )
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


HEURISTICAS = {"Manhattan": h_manhattan, "Euclidiana": h_euclidiana}


def construir_H(graph, goal, heuristica):
    """TABLA H como en el LAB 13: H[nodo] = h(nodo, meta)"""
    return {nodo: heuristica(nodo, goal) for nodo in graph}


# ===============================================================
# 7. FUNCIONES AUXILIARES
# ===============================================================
def reconstruct_path_dict(sol, start, goal):
    """reconstruct_path(sol, start, goal) DEL LAB 12/13"""
    if start == goal:
        return [start]
    path = [goal]
    s = goal
    while s:
        padre = sol[s]
        path.append(padre)
        s = padre
        if s == start:
            break
    return list(reversed(path))


def costo_camino(grid, camino):
    """Suma el costo de entrar a cada celda del camino (sin la inicial)."""
    return sum(COSTO_CELDA[int(grid[r][c])] for r, c in camino[1:])


class Resultado:
    def __init__(self, algoritmo, encontrado, camino, costo,
                 expandidos, generados, tiempo_ms):
        self.algoritmo = algoritmo
        self.encontrado = encontrado
        self.camino = camino
        self.costo = costo
        self.expandidos = expandidos
        self.generados = generados
        self.tiempo_ms = tiempo_ms

    @property
    def longitud(self):
        # NUMERO DE PASOS DEL CAMINO
        return max(len(self.camino) - 1, 0) if self.encontrado else 0


ALGORITMOS = ["BFS", "DFS", "Dijkstra", "A*", "Voraz"]


def _ejecutar(nombre, grid, graph, inicio, meta, heuristica, eventos):
    """Corre UN algoritmo y devuelve el camino (lista) o None."""
    if nombre == "BFS":
        problem = GridProblem(inicio, meta, grid)
        sol = breadth_first_search(problem, eventos)
        return reconstruct_path(sol) if sol is not None else None
    if nombre == "DFS":
        sol = dfs(graph, inicio, meta, eventos)
    elif nombre == "Dijkstra":
        sol, _ = minimo_costo(graph, inicio, meta, eventos)
    else:                                   # A* o Voraz
        H = construir_H(graph, meta, heuristica)
        sol, _ = astar(graph, H, inicio, meta, eventos, voraz=(nombre == "Voraz"))
    if sol is None or sol == []:
        return None
    return reconstruct_path_dict(sol, inicio, meta)


# ===============================================================
# 8. INTERFAZ DE USO PARA LA APLICACION
# ===============================================================
def eventos(nombre, grid, inicio, meta, heuristica=h_manhattan):
    """Lista de eventos para animar + ("fin", None) al final."""
    ev = []
    _ejecutar(nombre, grid, grid_a_grafo(grid), inicio, meta, heuristica, ev)
    ev.append(("fin", None))
    return ev


def resolver(nombre, grid, inicio, meta, heuristica=h_manhattan, repeticiones=3):
    graph = grid_a_grafo(grid)              # EL GRAFO SE DA ARMADO (no se cronometra)
    ev = []
    camino = _ejecutar(nombre, grid, graph, inicio, meta, heuristica, ev)
    expandidos = sum(1 for t, _ in ev if t == "expandir")
    generados = sum(1 for t, _ in ev if t == "frontera")
    # TIEMPO: mejor de `repeticiones` corridas SIN eventos
    mejor = float("inf")
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        _ejecutar(nombre, grid, graph, inicio, meta, heuristica, None)
        mejor = min(mejor, (time.perf_counter() - t0) * 1000)
    if camino is None:
        return Resultado(nombre, False, [], float("inf"), expandidos, generados, mejor)
    return Resultado(nombre, True, camino, costo_camino(grid, camino),
                     expandidos, generados, mejor)


def comparar(grid, inicio, meta, heuristica=h_manhattan):
    return [resolver(n, grid, inicio, meta, heuristica) for n in ALGORITMOS]


def tabla_texto(resultados):
    filas = [f"{'Algoritmo':<10}{'Costo':>8}{'Pasos':>8}{'Expand.':>9}{'Gener.':>9}{'Tiempo ms':>11}"]
    for r in resultados:
        if r.encontrado:
            filas.append(f"{r.algoritmo:<10}{r.costo:>8}{r.longitud:>8}{r.expandidos:>9}"
                         f"{r.generados:>9}{r.tiempo_ms:>11.3f}")
        else:
            filas.append(f"{r.algoritmo:<10}{'sin solucion':>16}{r.expandidos:>9}"
                         f"{r.generados:>9}{r.tiempo_ms:>11.3f}")
    return "\n".join(filas)


# ===============================================================
# TESTEO  (mismo mapa del LAB 11 + ejemplo de Rumania del LAB 12/13)
# ===============================================================
if __name__ == '__main__':
    grid = [
        [0, 1, 0, 0, 1, 0],
        [0, 1, 0, 2, 1, 0],
        [0, 0, 0, 2, 1, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0, 0],
    ]
    initial_state = (0, 0)
    goal_state = (0, 5)
    print("=== BFS (LAB 11) ===")
    problem = GridProblem(initial_state, goal_state, grid)
    solution_node = breadth_first_search(problem)
    if solution_node is not None:
        print('!! LLEGAMOS A LA META !!')
        print_complete_path(reconstruct_path(solution_node))
    else:
        print(" NO SE HALLO SOLUCION")

    graph = grid_a_grafo(grid)
    H = construir_H(graph, goal_state, h_manhattan)
    for nombre in ("DFS", "Dijkstra", "A*", "Voraz"):
        print(f"=== {nombre} ===")
        camino = _ejecutar(nombre, grid, graph, initial_state, goal_state,
                           h_manhattan, None)
        print("ruta :", camino)
        print("costo:", costo_camino(grid, camino) if camino else None)
