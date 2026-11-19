"""Genera capturas de la interfaz (sin ventana) para el informe y la presentación."""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import busqueda_clase as alg  # noqa: E402
import mapas  # noqa: E402
from app_busqueda import App, figura_comparacion  # noqa: E402

OUT = "figs"


def main():
    app = App(25, 41, semilla=3)
    ini, meta = app.inicio, app.meta
    print("Mapa base: terreno semilla 3 ->", ini, meta)
    print(alg.tabla_texto(alg.comparar(app.grid, ini, meta)))

    # Captura de la interfaz a mitad de animación (A*) y final de cada algoritmo
    app.radio_alg.set_active(3)
    app.preparar()
    app.avanzar(len(app.eventos) // 3)
    app.fig.savefig(f"{OUT}/ui_animacion_astar.png", dpi=110)

    for i, nombre in enumerate(app.ALGS):
        app.radio_alg.set_active(i)
        app.ejecutar_completo()
        app.fig.savefig(f"{OUT}/ui_{nombre.replace('*', 'star').lower()}.png", dpi=110)
        print(nombre, app.resultado.costo, app.resultado.expandidos)

    # Simulación de edición con el mouse (clic en una celda con la herramienta Pared)
    class Ev:  # evento falso mínimo
        inaxes = app.ax
        button = 1
        xdata, ydata = 10.2, 12.1
    app.radio_t.set_active(0)
    app._on_press(Ev())
    app._on_release(Ev())
    assert app.grid[12, 10] == mapas.PARED, "la edición con mouse no funcionó"
    print("Edición por mouse simulada: OK")

    # Comparación en la interfaz
    res = alg.comparar(app.grid, app.inicio, app.meta)
    figura_comparacion(res, "Comparación sobre el mapa actual (A*: Manhattan)").savefig(
        f"{OUT}/ui_comparacion.png", dpi=110)
    plt.close("all")


if __name__ == "__main__":
    main()
