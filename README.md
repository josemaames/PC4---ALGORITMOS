# PC4 – Métodos de búsqueda (C8277 Algoritmos y Estructuras de Datos)

BFS, DFS, Dijkstra, A* y Voraz sobre un mapa de cuadrícula con terreno
(libre = costo 1, barro = costo 5, pared = intransitable).
**El núcleo usa el código y las estructuras de los laboratorios del profesor.**

## Ejecutar (Windows: `python`, no `pip install` si ya los tienes)

```bash
python busqueda_clase.py        # demo por consola (mapa del Lab 11) - SOLO librería estándar
python test_clase.py            # pruebas con assert - SOLO librería estándar
pip install matplotlib numpy
python app_busqueda.py          # interfaz gráfica
python app_busqueda.py --filas 31 --cols 51 --semilla 7
```
Detener la interfaz: cerrar la ventana o `Ctrl + C` en la terminal.

## Qué es del curso y qué es opcional

| Archivo | Origen |
|---|---|
| `busqueda_clase.py` | NÚCLEO. BFS (Lab 11: Node, GridProblem, deque), DFS (Lab 9: myStack), Dijkstra (Lab 12: minimo_costo), A* y Voraz (Lab 13: astar + tabla H) |
| `estructuras_clase.py` | `myQueue` (circular) y `myStack` (Lab 9), `MinHeap` (Lab 7) |
| `app_busqueda.py` | OPCIONAL: interfaz matplotlib (animación, mouse, comparación) |
| `mapas.py` | OPCIONAL: generadores de mapas (numpy/random) |
| `test_clase.py`, `capturas.py` | pruebas simples / capturas para el informe |
| `opcional/` | benchmark, pruebas con pytest + networkx, versión v1 (generadores) |

Única corrección al código del profesor: al encontrar un camino más barato a un nodo que ya está
en la frontera, también se actualiza `parent[child] = node`.
