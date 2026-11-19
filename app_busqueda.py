"""
Visualizador de métodos de búsqueda (BFS, DFS, Dijkstra, A*, Voraz) - PC4 C8277.

Ejecutar:   python app_busqueda.py            (ventana interactiva)
Opciones:   --filas 25 --cols 41 --semilla 3

Uso:
  * Elige el algoritmo (y la heurística si es A*) y pulsa "Ejecutar".
  * Con el mouse (clic o arrastrar) edita el mapa según la herramienta elegida:
    Pared, Barro (costo 5), Borrar, Inicio, Meta.
  * "Comparar todos" corre los 5 algoritmos sobre el mapa actual y muestra gráficos.
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.widgets import Button, RadioButtons, Slider

import busqueda_clase as alg   # NUCLEO: codigo del profesor (BFS, DFS, Dijkstra, A*, Voraz)
import mapas                   # OPCIONAL: generadores de mapas

CMAP_BASE = ListedColormap(["#ffffff", "#2b2d42", "#c9a66b"])  # libre, pared, barro
COL_FRONTERA = (0.20, 0.60, 1.00, 0.60)
COL_EXPANDIDO = (0.60, 0.35, 0.90, 0.45)
COL_CAMINO = "#e63946"
COLORES_ALG = {"BFS": "#4c78a8", "DFS": "#f58518", "Dijkstra": "#54a24b", "A*": "#b279a2", "Voraz": "#e45756"}


class App:
    ALGS = list(alg.ALGORITMOS)
    HEURS = list(alg.HEURISTICAS)
    HERRAMIENTAS = ["Pared", "Barro", "Borrar", "Inicio", "Meta"]

    def __init__(self, filas=25, cols=41, semilla=3):
        self.filas, self.cols, self.semilla = filas, cols, semilla
        self.grid = mapas.generar_terreno(filas, cols, semilla)
        self.inicio = (1, 1)
        self.meta = (filas - 2, cols - 2)
        self.eventos, self.pos, self.resultado = [], 0, None
        self.es_front = np.zeros((filas, cols), bool)
        self.es_exp = np.zeros((filas, cols), bool)
        self.arrastrando = False
        self._construir_figura()
        self._refrescar_mapa()

    # ------------------------------------------------------------------ #
    # Construcción de la interfaz
    # ------------------------------------------------------------------ #
    def _construir_figura(self):
        self.fig = plt.figure(figsize=(14, 8))
        try:
            self.fig.canvas.manager.set_window_title("PC4 - Métodos de búsqueda")
        except Exception:
            pass

        # --- mapa ---
        self.ax = self.fig.add_axes([0.02, 0.07, 0.64, 0.88])
        self.im_base = self.ax.imshow(self.grid, cmap=CMAP_BASE, vmin=0, vmax=2,
                                      interpolation="nearest")
        self.im_ov = self.ax.imshow(np.zeros((self.filas, self.cols, 4)),
                                    interpolation="nearest")
        (self.linea,) = self.ax.plot([], [], color=COL_CAMINO, lw=3.2,
                                     solid_capstyle="round", solid_joinstyle="round")
        self.t_inicio = self.ax.text(0, 0, "S", ha="center", va="center", color="white",
                                     fontsize=11, fontweight="bold",
                                     bbox=dict(boxstyle="round,pad=0.25", fc="#2a9d8f", ec="none"))
        self.t_meta = self.ax.text(0, 0, "G", ha="center", va="center", color="white",
                                   fontsize=11, fontweight="bold",
                                   bbox=dict(boxstyle="round,pad=0.25", fc="#d62828", ec="none"))
        self.ax.set_xticks(np.arange(-0.5, self.cols, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.filas, 1), minor=True)
        self.ax.grid(which="minor", color="#d9d9d9", lw=0.4)
        self.ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
        self.ax.set_title("Mapa  (clic / arrastrar para editar)", fontsize=11)
        self.ax.legend(
            handles=[Patch(fc="#ffffff", ec="#999", label="Libre (1)"),
                     Patch(fc="#c9a66b", label="Barro (5)"),
                     Patch(fc="#2b2d42", label="Pared"),
                     Patch(fc=COL_FRONTERA, label="Frontera"),
                     Patch(fc=COL_EXPANDIDO, label="Expandido"),
                     Patch(fc=COL_CAMINO, label="Camino")],
            loc="upper center", bbox_to_anchor=(0.5, -0.005), ncol=6, fontsize=9, frameon=False)

        # --- controles ---
        ax_alg = self.fig.add_axes([0.69, 0.745, 0.13, 0.195])
        ax_alg.set_title("Algoritmo", fontsize=10, loc="left")
        self.radio_alg = RadioButtons(ax_alg, self.ALGS, active=3)
        ax_h = self.fig.add_axes([0.84, 0.80, 0.14, 0.14])
        ax_h.set_title("Heurística (A*)", fontsize=10, loc="left")
        self.radio_h = RadioButtons(ax_h, self.HEURS, active=0)
        ax_t = self.fig.add_axes([0.69, 0.50, 0.13, 0.21])
        ax_t.set_title("Editar con el mouse", fontsize=10, loc="left")
        self.radio_t = RadioButtons(ax_t, self.HERRAMIENTAS, active=0)
        for r in (self.radio_alg, self.radio_h, self.radio_t):
            for t in r.labels:
                t.set_fontsize(11)
        self.radio_alg.on_clicked(lambda _: self._parar_y_limpiar())
        self.radio_h.on_clicked(lambda _: self._parar_y_limpiar())

        ax_v = self.fig.add_axes([0.79, 0.455, 0.18, 0.025])
        self.sl_vel = Slider(ax_v, "Velocidad ", 1, 60, valinit=10, valstep=1)

        self.botones = {}
        def boton(nombre, rect, accion, color="#e8e8e8"):
            b = Button(self.fig.add_axes(rect), nombre, color=color, hovercolor="#cfd8dc")
            b.on_clicked(accion)
            self.botones[nombre] = b
        boton("Ejecutar", [0.69, 0.385, 0.13, 0.05], self._on_ejecutar, "#b7e4c7")
        boton("Limpiar búsqueda", [0.84, 0.385, 0.14, 0.05], lambda _: self._parar_y_limpiar())
        boton("Laberinto", [0.69, 0.32, 0.13, 0.05], lambda _: self._nuevo_mapa("laberinto"))
        boton("Aleatorio", [0.84, 0.32, 0.14, 0.05], lambda _: self._nuevo_mapa("aleatorio"))
        boton("Terreno", [0.69, 0.255, 0.13, 0.05], lambda _: self._nuevo_mapa("terreno"))
        boton("Mapa vacío", [0.84, 0.255, 0.14, 0.05], lambda _: self._nuevo_mapa("vacio"))
        boton("Comparar todos", [0.69, 0.19, 0.29, 0.05], self._on_comparar, "#ffe8a3")

        self.ax_info = self.fig.add_axes([0.69, 0.02, 0.29, 0.15])
        self.ax_info.axis("off")
        self.txt_info = self.ax_info.text(0, 1, "", va="top", ha="left", family="monospace",
                                          fontsize=10)

        # --- mouse y temporizador ---
        self.fig.canvas.mpl_connect("button_press_event", self._on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_move)
        self.fig.canvas.mpl_connect("button_release_event", self._on_release)
        self.timer = self.fig.canvas.new_timer(interval=30)
        self.timer.add_callback(self._tick)

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def _refrescar_mapa(self):
        self.im_base.set_data(self.grid)
        self.t_inicio.set_position((self.inicio[1], self.inicio[0]))
        self.t_meta.set_position((self.meta[1], self.meta[0]))
        self._pintar_overlay()
        self._info("Elige un algoritmo y pulsa Ejecutar.")

    def _pintar_overlay(self):
        ov = np.zeros((self.filas, self.cols, 4))
        ov[self.es_front] = COL_FRONTERA
        ov[self.es_exp] = COL_EXPANDIDO
        self.im_ov.set_data(ov)
        self.fig.canvas.draw_idle()

    def _info(self, texto):
        self.txt_info.set_text(texto)
        self.fig.canvas.draw_idle()

    def _texto_resultado(self, r, nombre_h):
        etiqueta = f"{r.algoritmo} ({nombre_h})" if r.algoritmo == "A*" else r.algoritmo
        if r.encontrado:
            return (f"Algoritmo : {etiqueta}\nResultado : camino encontrado\n"
                    f"Costo     : {r.costo}\nPasos     : {r.longitud}\n"
                    f"Expandidos: {r.expandidos}\nGenerados : {r.generados}\n"
                    f"Tiempo    : {r.tiempo_ms:.3f} ms")
        return (f"Algoritmo : {etiqueta}\nResultado : SIN SOLUCIÓN\n"
                f"Expandidos: {r.expandidos}\nGenerados : {r.generados}\n"
                f"Tiempo    : {r.tiempo_ms:.3f} ms")

    # ------------------------------------------------------------------ #
    # Búsqueda
    # ------------------------------------------------------------------ #
    def _heuristica(self):
        return alg.HEURISTICAS[self.radio_h.value_selected]

    def _limpiar_busqueda(self):
        self.eventos, self.pos, self.resultado = [], 0, None
        self.es_front[:] = False
        self.es_exp[:] = False
        self.linea.set_data([], [])

    def _parar_y_limpiar(self):
        self.timer.stop()
        self._limpiar_busqueda()
        self._pintar_overlay()
        self._info("Elige un algoritmo y pulsa Ejecutar.")

    def preparar(self):
        """Calcula resultado (con tiempo) y la lista de eventos a animar."""
        self.timer.stop()
        self._limpiar_busqueda()
        nombre, h = self.radio_alg.value_selected, self._heuristica()
        self.resultado = alg.resolver(nombre, self.grid, self.inicio, self.meta, h)
        self.eventos = alg.eventos(nombre, self.grid, self.inicio, self.meta, h)
        self.pos = 0

    def avanzar(self, n):
        """Procesa hasta `n` eventos. Devuelve True si la animación terminó."""
        fin = False
        for _ in range(n):
            if self.pos >= len(self.eventos):
                fin = True
                break
            tipo, dato = self.eventos[self.pos]
            self.pos += 1
            if tipo == "frontera":
                self.es_front[dato] = True
            elif tipo == "expandir":
                self.es_exp[dato] = True
                self.es_front[dato] = False
            else:  # fin
                fin = True
        self._pintar_overlay()
        if fin:
            self._mostrar_final()
        else:
            self._info(f"Buscando...\nExpandidos: {int(self.es_exp.sum())}\n"
                       f"En frontera: {int(self.es_front.sum())}")
        return fin

    def _mostrar_final(self):
        r = self.resultado
        if r.encontrado:
            ys, xs = zip(*r.camino)
            self.linea.set_data(xs, ys)
        self._info(self._texto_resultado(r, self.radio_h.value_selected))

    def _tick(self):
        if self.avanzar(int(self.sl_vel.val)):
            self.timer.stop()

    def _on_ejecutar(self, _evento=None):
        self.preparar()
        self.timer.start()

    def ejecutar_completo(self):
        """Corre la búsqueda completa sin animar (útil para capturas y pruebas)."""
        self.preparar()
        self.avanzar(len(self.eventos))

    # ------------------------------------------------------------------ #
    # Mapas y edición
    # ------------------------------------------------------------------ #
    def _nuevo_mapa(self, tipo):
        self.timer.stop()
        self._limpiar_busqueda()
        self.semilla += 1
        f, c, s = self.filas, self.cols, self.semilla
        if tipo == "laberinto":
            self.grid = mapas.generar_laberinto(f, c, s)
        elif tipo == "aleatorio":
            self.grid = mapas.generar_aleatorio(f, c, semilla=s)
        elif tipo == "terreno":
            self.grid = mapas.generar_terreno(f, c, s)
        else:
            self.grid = np.zeros((f, c), dtype=np.int8)
        self.inicio, self.meta = (1, 1), (f - 2, c - 2)
        self._refrescar_mapa()

    def _celda(self, ev):
        if ev.inaxes is not self.ax or ev.xdata is None:
            return None
        c, r = int(round(ev.xdata)), int(round(ev.ydata))
        return (r, c) if 0 <= r < self.filas and 0 <= c < self.cols else None

    def _on_press(self, ev):
        if ev.button == 1 and self._celda(ev) is not None:
            self.arrastrando = True
            self._editar(self._celda(ev))

    def _on_move(self, ev):
        if self.arrastrando and self._celda(ev) is not None:
            self._editar(self._celda(ev))

    def _on_release(self, _ev):
        self.arrastrando = False

    def _editar(self, celda):
        herramienta = self.radio_t.value_selected
        if herramienta == "Inicio":
            if self.grid[celda] != mapas.PARED and celda != self.meta:
                self.inicio = celda
        elif herramienta == "Meta":
            if self.grid[celda] != mapas.PARED and celda != self.inicio:
                self.meta = celda
        elif celda not in (self.inicio, self.meta):
            self.grid[celda] = {"Pared": mapas.PARED, "Barro": mapas.BARRO,
                                "Borrar": mapas.LIBRE}[herramienta]
        else:
            return
        self.timer.stop()
        self._limpiar_busqueda()
        self._refrescar_mapa()

    # ------------------------------------------------------------------ #
    # Comparación
    # ------------------------------------------------------------------ #
    def _on_comparar(self, _evento=None):
        res = alg.comparar(self.grid, self.inicio, self.meta, self._heuristica())
        print(alg.tabla_texto(res))
        fig = figura_comparacion(res, f"Comparación sobre el mapa actual "
                                      f"(A*: {self.radio_h.value_selected})")
        fig.show()


def figura_comparacion(resultados, titulo="Comparación de algoritmos"):
    """3 gráficos de barras: nodos expandidos, costo del camino y tiempo."""
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
    nombres = [r.algoritmo for r in resultados]
    colores = [COLORES_ALG[n] for n in nombres]
    datos = [("Nodos expandidos", [r.expandidos for r in resultados], "{:d}"),
             ("Costo del camino", [r.costo if r.encontrado else 0 for r in resultados], "{:.0f}"),
             ("Tiempo (ms)", [r.tiempo_ms for r in resultados], "{:.2f}")]
    for ax, (nombre, valores, fmt) in zip(axs, datos):
        barras = ax.bar(nombres, valores, color=colores)
        ax.set_title(nombre, fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        for b, v in zip(barras, valores):
            ax.annotate(fmt.format(int(v) if fmt == "{:d}" else v),
                        (b.get_x() + b.get_width() / 2, b.get_height()),
                        ha="center", va="bottom", fontsize=9, xytext=(0, 2),
                        textcoords="offset points")
        ax.margins(y=0.15)
    if not all(r.encontrado for r in resultados):
        fig.text(0.5, 0.01, "Algún algoritmo no encontró camino (costo mostrado como 0).",
                 ha="center", fontsize=9, color="#b00020")
    fig.suptitle(titulo, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig


def main():
    p = argparse.ArgumentParser(description="Visualizador de métodos de búsqueda")
    p.add_argument("--filas", type=int, default=25)
    p.add_argument("--cols", type=int, default=41)
    p.add_argument("--semilla", type=int, default=3)
    a = p.parse_args()
    app = App(a.filas, a.cols, a.semilla)  # noqa: F841 (mantiene vivos los widgets)
    plt.show()


if __name__ == "__main__":
    main()
