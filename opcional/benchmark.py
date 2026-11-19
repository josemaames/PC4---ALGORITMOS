"""Experimentos para el informe: escenarios, escalado y heurísticas. Guarda figs/ y results.json"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import busqueda_clase as alg  # noqa: E402  (codigo del profesor)
import mapas  # noqa: E402
from app_busqueda import COLORES_ALG, figura_comparacion  # noqa: E402

F, C = 25, 41
salida = {}


def extremos(g):
    return (1, 1), (g.shape[0] - 2, g.shape[1] - 2)


# ---------------------------------------------------------------- escenarios
escenarios = {
    "Mapa vacío": np.zeros((F, C), dtype=np.int8),
    "Laberinto": mapas.generar_laberinto(F, C, 11),
    "Aleatorio": mapas.generar_aleatorio(F, C, 0.22, 0.12, 5),
    "Terreno": mapas.generar_terreno(F, C, 3),
}
salida["escenarios"] = {}
for nombre, g in escenarios.items():
    ini, meta = extremos(g)
    res = alg.comparar(g, ini, meta)
    print(f"\n== {nombre} ==")
    print(alg.tabla_texto(res))
    salida["escenarios"][nombre] = [
        dict(alg=r.algoritmo, ok=r.encontrado, costo=r.costo if r.encontrado else None,
             pasos=r.longitud, expandidos=r.expandidos, generados=r.generados,
             tiempo_ms=round(r.tiempo_ms, 3)) for r in res]
    fig = figura_comparacion(res, f"Escenario: {nombre}")
    fig.savefig(f"figs/esc_{nombre.lower().replace(' ', '_').replace('í', 'i')}.png", dpi=110)
    plt.close(fig)

# panel con los 4 mapas y el camino de A*
fig, axs = plt.subplots(1, 4, figsize=(16, 3.6))
for ax, (nombre, g) in zip(axs, escenarios.items()):
    ini, meta = extremos(g)
    r = alg.resolver("A*", g, ini, meta, repeticiones=1)
    ax.imshow(g, cmap=matplotlib.colors.ListedColormap(["#ffffff", "#2b2d42", "#c9a66b"]),
              vmin=0, vmax=2, interpolation="nearest")
    if r.encontrado:
        ys, xs = zip(*r.camino)
        ax.plot(xs, ys, color="#e63946", lw=2)
    ax.plot(ini[1], ini[0], "s", color="#2a9d8f", ms=8)
    ax.plot(meta[1], meta[0], "s", color="#d62828", ms=8)
    ax.set_title(nombre, fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle("Escenarios probados (camino óptimo de A*)", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig("figs/escenarios.png", dpi=110)
plt.close(fig)

# ---------------------------------------------------------------- escalado
tamanos = [20, 40, 60, 80, 100]
SEMILLAS = range(12)
esc = {n: {t: dict(exp=[], ms=[]) for t in alg.ALGORITMOS} for n in tamanos}
for n in tamanos:
    for s in SEMILLAS:
        g = mapas.generar_aleatorio(n, n, 0.20, 0.10, s)
        ini, meta = extremos(g)
        rs = {t: alg.resolver(t, g, ini, meta, repeticiones=1) for t in alg.ALGORITMOS}
        if not rs["Dijkstra"].encontrado:
            continue
        for t, r in rs.items():
            esc[n][t]["exp"].append(r.expandidos)
            esc[n][t]["ms"].append(r.tiempo_ms)
salida["escalado"] = {
    str(n): {t: dict(exp=float(np.mean(v["exp"])), ms=float(np.mean(v["ms"])), n=len(v["exp"]))
             for t, v in d.items()} for n, d in esc.items()}
print("\n== Escalado (promedio de mapas resolubles) ==")
for n in tamanos:
    print(n, {t: round(salida["escalado"][str(n)][t]["exp"]) for t in alg.ALGORITMOS},
          "mapas:", salida["escalado"][str(n)]["BFS"]["n"])

fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
for t in alg.ALGORITMOS:
    axs[0].plot(tamanos, [salida["escalado"][str(n)][t]["exp"] for n in tamanos],
                "o-", color=COLORES_ALG[t], label=t)
    axs[1].plot(tamanos, [salida["escalado"][str(n)][t]["ms"] for n in tamanos],
                "o-", color=COLORES_ALG[t], label=t)
axs[0].set_title("Nodos expandidos vs tamaño (n×n)")
axs[1].set_title("Tiempo (ms) vs tamaño (n×n)")
for ax in axs:
    ax.set_xlabel("n"); ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figs/escalado.png", dpi=110)
plt.close(fig)

# ---------------------------------------------------------------- heurísticas
acum = {"Dijkstra (h=0)": [], "A* Euclidiana": [], "A* Manhattan": []}
costos_iguales = True
for s in range(30):
    g = mapas.generar_aleatorio(40, 40, 0.20, 0.10, s)
    ini, meta = extremos(g)
    rd = alg.resolver("Dijkstra", g, ini, meta, repeticiones=1)
    if not rd.encontrado:
        continue
    re_ = alg.resolver("A*", g, ini, meta, alg.h_euclidiana, repeticiones=1)
    rm = alg.resolver("A*", g, ini, meta, alg.h_manhattan, repeticiones=1)
    costos_iguales &= (rd.costo == re_.costo == rm.costo)
    acum["Dijkstra (h=0)"].append(rd.expandidos)
    acum["A* Euclidiana"].append(re_.expandidos)
    acum["A* Manhattan"].append(rm.expandidos)
salida["heuristicas"] = {k: float(np.mean(v)) for k, v in acum.items()}
salida["heuristicas"]["mapas"] = len(acum["A* Manhattan"])
salida["heuristicas"]["costos_iguales"] = bool(costos_iguales)
print("\n== Heurísticas (40x40) ==", salida["heuristicas"])

fig, ax = plt.subplots(figsize=(6.5, 4))
vals = [np.mean(v) for v in acum.values()]
barras = ax.bar(list(acum), vals, color=["#54a24b", "#9ecae9", "#b279a2"])
for b, v in zip(barras, vals):
    ax.annotate(f"{v:.0f}", (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom",
                xytext=(0, 2), textcoords="offset points")
ax.set_title("Nodos expandidos según la heurística (mapas 40×40)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("figs/heuristicas.png", dpi=110)
plt.close(fig)

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
