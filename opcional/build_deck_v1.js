const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "PC4 - Métodos de búsqueda";
pres.author = "José Manuel Ames";
pres.subject = "C8277 Algoritmos y Estructuras de Datos";

const THEME = {
  name: "Busqueda",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1D2E", lt1: "FFFFFF", dk2: "4A4E69", lt2: "EEF1F5",
    accent1: "E63946", // camino
    accent2: "B279A2", // A*
    accent3: "C9A66B", // barro
    accent4: "4C78A8", // BFS
    accent5: "F58518", // DFS
    accent6: "54A24B", // Dijkstra
    hlink: "4C78A8", folHlink: "4A4E69",
  },
};
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const HEX = { text1: "1B1D2E", text2: "4A4E69", BFS: "4C78A8", DFS: "F58518", Dijkstra: "54A24B", "A*": "B279A2", grid: "E5E7EB" };
const ALGC = { BFS: C.accent4, DFS: C.accent5, Dijkstra: C.accent6, "A*": C.accent2 };
const FOOT = "PC4 · C8277 Algoritmos y Estructuras de Datos";

// ------------------------------------------------------------------ layouts
const footer = [
  { text: { text: FOOT, options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 11, color: C.text2, margin: 0 } } },
];
pres.defineSlideMaster({
  title: "PORTADA",
  objects: [
    { rect: { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: C.text1 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.5, w: 11.7, h: 1.7, fontSize: 44, bold: true, color: C.background1, align: "left", valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.4, w: 11.7, h: 1.8, fontSize: 20, color: C.background2, align: "left", valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: "FFFFFF" },
  margin: [0.4, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 34, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: "" } },
    ...footer,
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 11, color: C.text2, align: "right" },
});
pres.defineSlideMaster({
  title: "OSCURO",
  objects: [
    { rect: { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: C.text1 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 34, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ helpers
const T = (s, text, o = {}) => s.addText(text, Object.assign({ isTextBox: true, margin: 0, color: C.text1, valign: "top" }, o));
const card = (s, x, y, w, h, name, fill = C.background2) =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { type: "none" }, objectName: name });
const dot = (s, x, y, d, color, name) =>
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color }, line: { type: "none" }, objectName: name });
const newSlide = (layout, section) => pres.addSlide({ masterName: layout, sectionTitle: section });
const chartText = (size, color = HEX.text2) => ({ fontSize: size, color, fontFace: "+mn-lt" });

// ================================================================== 1. Portada
pres.addSection({ title: "Introducción" });
let s = newSlide("PORTADA", "Introducción");
s.addText("Métodos de búsqueda sobre una cuadrícula con terreno", { placeholder: "title" });
s.addText([
  { text: "BFS · DFS · Dijkstra · A*", options: { breakLine: true, bold: true } },
  { text: "PC4 — C8277 Algoritmos y Estructuras de Datos · Exposición: 24 de noviembre", options: { breakLine: true } },
  { text: "José Manuel Ames Anapán · Isabel Antonella Padilla Romero · Nardy Liz Condori Mamani" },
], { placeholder: "body" });
{
  const patron = ["PPPP.mm...", "...PP.mm..", ".mm.PPPP..", ".mm....PPP"];
  const paso = 0.46;
  patron.forEach((fila, r) => [...fila].forEach((ch, c) => {
    const fill = ch === "P" ? { color: C.accent1 } : ch === "m" ? { color: C.accent3 } : { color: C.background1, transparency: 88 };
    s.addShape(pres.ShapeType.rect, { x: 8.2 + c * paso, y: 0.6 + r * paso, w: 0.4, h: 0.4, fill, line: { type: "none" }, objectName: `celda-${r}-${c}` });
  }));
}
s.addNotes("Presentación de la PC4. Resumen: implementamos un visualizador interactivo de BFS, DFS, Dijkstra y A* sobre un mapa de cuadrícula con terreno, y lo evaluamos con experimentos y pruebas.");

// ================================================================== 2. Problema
s = newSlide("CONTENIDO", "Introducción");
s.addText("Qué pide el enunciado y qué hicimos", { placeholder: "title" });
T(s, [
  { text: "Qué pide el enunciado", options: { bold: true, fontSize: 20, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Implementar una aplicación con métodos de búsqueda", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Mostrar resultados con interfaz de usuario y herramientas gráficas", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Explicar las librerías y sus funciones", options: { bullet: true, breakLine: true, paraSpaceAfter: 18 } },
  { text: "Qué hicimos", options: { bold: true, fontSize: 20, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Visualizador interactivo en Python (matplotlib + numpy)", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "BFS, DFS, Dijkstra y A* sobre un mismo mapa con terreno", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Animación paso a paso, edición con el mouse y comparación", options: { bullet: true } },
], { x: 0.6, y: 1.6, w: 5.9, h: 4.8, fontSize: 18, objectName: "texto-problema" });
s.addImage({ path: "/home/claude/pc4/figs/ui_astar.png", x: 6.9, y: 1.7, w: 5.85, h: 3.34, altText: "Captura de la aplicación con A* resuelto sobre un mapa con barro y paredes", objectName: "captura-app" });
T(s, "La aplicación con A* sobre el terreno de ejemplo", { x: 6.9, y: 5.15, w: 5.85, h: 0.3, fontSize: 12, color: C.text2, objectName: "pie-captura" });
s.addNotes("El enunciado pide una aplicación de búsqueda con interfaz gráfica y explicar las librerías. Nuestra solución es un visualizador en Python que corre los cuatro métodos sobre el mismo mapa.");

// ================================================================== 3. Modelo del mapa
s = newSlide("CONTENIDO", "Introducción");
s.addText("El mapa: tres tipos de celda", { placeholder: "title" });
[
  { nombre: "Libre", num: "1", sub: "costo de entrar", fill: C.background1, linea: true },
  { nombre: "Barro", num: "5", sub: "costo de entrar", fill: C.accent3 },
  { nombre: "Pared", num: "∞", sub: "intransitable", fill: C.text1 },
].forEach((c, i) => {
  const x = 0.6 + i * 4.14;
  card(s, x, 1.7, 3.85, 3.0, `tarjeta-${c.nombre.toLowerCase()}`);
  s.addShape(pres.ShapeType.rect, { x: x + 0.35, y: 2.05, w: 0.8, h: 0.8, fill: { color: c.fill }, line: c.linea ? { color: C.text2, width: 1.25 } : { type: "none" }, objectName: `muestra-${c.nombre.toLowerCase()}` });
  T(s, c.nombre, { x: x + 1.4, y: 2.15, w: 2.2, h: 0.6, fontSize: 26, bold: true, valign: "middle" });
  T(s, c.num, { x: x + 0.35, y: 3.0, w: 3.1, h: 1.0, fontSize: 60, bold: true, valign: "middle" });
  T(s, c.sub, { x: x + 0.35, y: 4.05, w: 3.1, h: 0.4, fontSize: 16, color: C.text2 });
});
T(s, [
  { text: "Movimientos: arriba, derecha, abajo e izquierda. El costo de un paso es el de la celda a la que se entra.", options: { breakLine: true, paraSpaceAfter: 8 } },
  { text: "Con costos uniformes BFS ya es óptimo; el barro hace visible la diferencia entre minimizar pasos y minimizar costo." },
], { x: 0.6, y: 5.1, w: 12.1, h: 1.5, fontSize: 18, objectName: "texto-reglas" });
s.addNotes("Las celdas libres cuestan 1, el barro cuesta 5 y las paredes no se pueden cruzar. El barro es lo que permite distinguir los algoritmos que minimizan pasos de los que minimizan costo.");

// ================================================================== 4. Los cuatro métodos
pres.addSection({ title: "Métodos" });
s = newSlide("CONTENIDO", "Métodos");
s.addText("Los cuatro métodos de búsqueda", { placeholder: "title" });
[
  ["BFS", "Amplitud", "Cola FIFO, expande por niveles", "Mínimos pasos; óptimo en costo solo con costos iguales", "O(V + E)"],
  ["DFS", "Profundidad", "Pila LIFO, baja por una rama", "No garantiza el camino más corto", "O(V + E)"],
  ["Dijkstra", "Costo uniforme", "Heap ordenado por g(n)", "Óptimo; no usa información de la meta", "O((V + E) log V)"],
  ["A*", "Con heurística", "Heap ordenado por g(n) + h(n)", "Óptimo con h admisible; expande menos nodos", "O((V + E) log V)"],
].forEach(([clave, nombre, estructura, optimo, coste], i) => {
  const x = 0.6 + (i % 2) * 6.2, y = 1.6 + Math.floor(i / 2) * 2.65;
  card(s, x, y, 5.9, 2.4, `tarjeta-${clave}`);
  dot(s, x + 0.3, y + 0.32, 0.34, ALGC[clave], `marca-${clave}`);
  T(s, [{ text: clave, options: { bold: true, fontSize: 22 } }, { text: `  ${nombre}`, options: { fontSize: 16, color: C.text2 } }], { x: x + 0.8, y: y + 0.25, w: 4.8, h: 0.5, valign: "middle" });
  T(s, [
    { text: estructura, options: { breakLine: true, paraSpaceAfter: 6 } },
    { text: optimo, options: { breakLine: true, paraSpaceAfter: 6 } },
    { text: `Tiempo: ${coste}`, options: { color: C.text2 } },
  ], { x: x + 0.3, y: y + 0.9, w: 5.3, h: 1.4, fontSize: 16 });
});
s.addNotes("Los cuatro recorren el mismo grafo; solo cambia cómo eligen el siguiente nodo. BFS y DFS usan cola y pila; Dijkstra y A* usan una cola de prioridad. A* añade una heurística que guía la búsqueda hacia la meta.");

// ================================================================== 5. A* y heurísticas
s = newSlide("CONTENIDO", "Métodos");
s.addText("A*: lo recorrido más lo que falta", { placeholder: "title" });
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 1.6, w: 7.5, h: 1.3, rectRadius: 0.12, fill: { color: C.text1 }, line: { type: "none" }, objectName: "formula-fondo" });
T(s, "f(n) = g(n) + h(n)", { x: 0.6, y: 1.6, w: 7.5, h: 1.3, fontSize: 40, bold: true, color: C.background1, align: "center", valign: "middle", fontFace: "Cambria", objectName: "formula" });
T(s, "g(n): costo ya recorrido · h(n): estimación hasta la meta", { x: 0.6, y: 3.05, w: 7.5, h: 0.4, fontSize: 16, color: C.text2 });
[
  ["Manhattan", "|Δfila| + |Δcol|", "Más informada: poda más"],
  ["Euclidiana", "√(Δfila² + Δcol²)", "Admisible, poda menos"],
].forEach(([nombre, formula, nota], i) => {
  const x = 0.6 + i * 3.85;
  card(s, x, 3.7, 3.65, 2.2, `tarjeta-${nombre.toLowerCase()}`);
  T(s, nombre, { x: x + 0.3, y: 3.9, w: 3.1, h: 0.4, fontSize: 20, bold: true });
  T(s, formula, { x: x + 0.3, y: 4.45, w: 3.1, h: 0.5, fontSize: 22, fontFace: "Cambria" });
  T(s, nota, { x: x + 0.3, y: 5.1, w: 3.1, h: 0.6, fontSize: 15, color: C.text2 });
});
card(s, 8.5, 1.6, 4.23, 4.3, "panel-estadistica");
T(s, "404", { x: 8.8, y: 1.85, w: 3.6, h: 1.2, fontSize: 80, bold: true, color: C.accent1, valign: "middle" });
T(s, "nodos expandidos de media con A* Manhattan", { x: 8.8, y: 3.05, w: 3.6, h: 0.7, fontSize: 16 });
T(s, "1271", { x: 8.8, y: 3.95, w: 3.6, h: 0.8, fontSize: 48, bold: true, color: C.text2, valign: "middle" });
T(s, "con Dijkstra (misma solución óptima)", { x: 8.8, y: 4.8, w: 3.6, h: 0.5, fontSize: 16 });
T(s, "Promedio de 30 mapas de 40×40", { x: 8.8, y: 5.4, w: 3.6, h: 0.3, fontSize: 12, color: C.text2 });
s.addNotes("Ambas heurísticas son admisibles y consistentes porque el paso mínimo cuesta 1 y solo hay 4 movimientos. Manhattan es mayor o igual que la euclidiana, por eso poda más. Con h = 0, A* es Dijkstra.");

// ================================================================== 6. Arquitectura
s = newSlide("CONTENIDO", "Métodos");
s.addText("Arquitectura: los algoritmos emiten eventos", { placeholder: "title" });
const caja = (x, y, w, h, titulo, detalle, name, oscuro = false) => {
  card(s, x, y, w, h, name, oscuro ? C.text1 : C.background2);
  T(s, [
    { text: titulo, options: { bold: true, fontSize: 20, breakLine: true, paraSpaceAfter: 4 } },
    { text: detalle, options: { fontSize: 15 } },
  ], { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: h - 0.4, color: oscuro ? C.background1 : C.text1, valign: "middle" });
};
caja(0.6, 2.2, 3.3, 2.1, "Mapas", "laberinto · aleatorio · terreno · vacío", "caja-mapas");
caja(4.9, 2.2, 3.4, 2.1, "Algoritmos", "BFS, DFS, Dijkstra y A* como generadores", "caja-algoritmos", true);
caja(9.7, 1.9, 3.03, 1.3, "Interfaz", "animación y panel", "caja-interfaz");
caja(9.7, 3.4, 3.03, 1.3, "Medición", "resolver() y comparar()", "caja-medicion");
const flecha = (x1, y1, x2, name) => s.addShape(pres.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: 0, line: { color: C.text2, width: 2.5, endArrowType: "triangle" }, objectName: name });
flecha(3.95, 3.25, 4.85, "flecha-mapas");
flecha(8.35, 2.55, 9.65, "flecha-interfaz");
flecha(8.35, 4.05, 9.65, "flecha-medicion");
T(s, "Eventos que emite cada algoritmo", { x: 4.9, y: 4.6, w: 3.4, h: 0.3, fontSize: 14, color: C.text2, align: "center" });
["frontera", "expandir", "fin"].forEach((ev, i) => {
  s.addText(ev, { x: 4.0 + i * 1.75, y: 5.0, w: 1.6, h: 0.42, shape: pres.ShapeType.roundRect, rectRadius: 0.1, fill: { color: C.background2 }, color: C.text1, fontFace: "Courier New", fontSize: 15, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `evento-${ev}` });
});
T(s, "Lo que se ve en pantalla es exactamente lo que se midió: la misma función alimenta la animación y las estadísticas.", { x: 0.6, y: 5.85, w: 12.1, h: 0.8, fontSize: 18, objectName: "texto-idea" });
s.addNotes("Cada algoritmo es un generador que emite eventos: frontera cuando un nodo entra a la estructura, expandir cuando se saca y fin con el resultado. La interfaz anima esos eventos y la función resolver los consume para medir tiempo y estadísticas.");

// ================================================================== 7. Librerías
pres.addSection({ title: "Implementación" });
s = newSlide("CONTENIDO", "Implementación");
s.addText("Librerías y funciones clave", { placeholder: "title" });
[
  ["numpy", ["np.full, np.zeros: crean el mapa y las capas", "default_rng: azar reproducible", "Máscaras booleanas: pintan celdas sin bucles", ".shape y .sum(): tamaño y conteos"]],
  ["matplotlib", ["add_axes: coloca cada zona", "imshow: dibuja la matriz de celdas", "ListedColormap: valores a colores", "plot, text, savefig: camino, marcas y capturas"]],
  ["widgets y eventos", ["RadioButtons, Button, Slider: controles", "mpl_connect: clic y arrastre", "new_timer: reloj de la animación", ".value_selected y .val: leen la opción"]],
  ["biblioteca estándar", ["heapq: cola de prioridad", "deque: cola FIFO de BFS", "dataclass: clase Resultado", "math.hypot, random, perf_counter"]],
].forEach(([nombre, items], i) => {
  const x = 0.6 + i * 3.07;
  card(s, x, 1.6, 2.9, 4.4, `tarjeta-${nombre}`);
  T(s, nombre, { x: x + 0.25, y: 1.85, w: 2.4, h: 0.7, fontSize: 20, bold: true });
  T(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1, paraSpaceAfter: 10 } })), { x: x + 0.25, y: 2.65, w: 2.45, h: 3.1, fontSize: 15 });
});
T(s, "Solo para validar: networkx (costo óptimo independiente) y pytest (8 pruebas).", { x: 0.6, y: 6.2, w: 12.1, h: 0.4, fontSize: 16, color: C.text2, objectName: "nota-validacion" });
s.addNotes("La aplicación solo necesita matplotlib y numpy. Heapq da la cola de prioridad de Dijkstra y A*, y deque la cola de BFS. Networkx y pytest se usan únicamente para validar los resultados.");

// ================================================================== 8. Interfaz
s = newSlide("CONTENIDO", "Implementación");
s.addText("La interfaz", { placeholder: "title" });
s.addImage({ path: "/home/claude/pc4/figs/ui_animacion_astar.png", x: 0.6, y: 1.55, w: 8.2, h: 4.69, altText: "Captura de la interfaz con A* a un tercio de la búsqueda: frontera en azul y nodos expandidos en lila", objectName: "captura-animacion" });
T(s, "A* a un tercio de la búsqueda: azul = frontera, lila = expandidos", { x: 0.6, y: 6.35, w: 8.2, h: 0.3, fontSize: 12, color: C.text2, objectName: "pie-animacion" });
[
  ["Elige algoritmo y heurística", "BFS, DFS, Dijkstra o A*"],
  ["Edita con el mouse", "Pared, barro, inicio y meta"],
  ["Mira la búsqueda", "Frontera, expandidos y camino"],
  ["Compara los cuatro", "Un clic y gráfico de barras"],
].forEach(([titulo, detalle], i) => {
  const y = 1.6 + i * 1.18;
  s.addText(String(i + 1), { x: 9.2, y, w: 0.55, h: 0.55, shape: pres.ShapeType.ellipse, fill: { color: C.text1 }, color: C.background1, fontSize: 18, bold: true, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `numero-${i + 1}` });
  T(s, [{ text: titulo, options: { bold: true, fontSize: 18, breakLine: true } }, { text: detalle, options: { fontSize: 15, color: C.text2 } }], { x: 9.95, y: y - 0.02, w: 2.8, h: 1.0 });
});
s.addNotes("Demostrar: elegir algoritmo, pulsar Ejecutar, ajustar la velocidad, editar el mapa con el mouse y usar Comparar todos.");

// ================================================================== 9. Resultado en terreno
pres.addSection({ title: "Resultados" });
s = newSlide("CONTENIDO", "Resultados");
s.addText("Con barro, BFS paga casi el doble", { placeholder: "title" });
const colores = [HEX.BFS, HEX.DFS, HEX.Dijkstra, HEX["A*"]];
const barras = (x, titulo, valores) => s.addChart(pres.charts.BAR, [{ name: titulo, labels: ["BFS", "DFS", "Dijkstra", "A*"], values: valores }], {
  x, y: 1.55, w: 5.9, h: 4.6, barDir: "col", chartColors: colores, barGapWidthPct: 55,
  showTitle: true, title: titulo, titleFontSize: 18, titleColor: HEX.text1, titleFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 14, dataLabelColor: HEX.text1, dataLabelFontFace: "+mn-lt",
  catAxisLabelFontSize: 14, catAxisLabelColor: HEX.text2, catAxisLabelFontFace: "+mn-lt",
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
});
barras(0.6, "Costo del camino", [120, 126, 62, 62]);
barras(6.83, "Nodos expandidos", [957, 67, 832, 239]);
T(s, "Mapa de terreno 25×41. Dijkstra y A* coinciden en el costo óptimo (62); A* llega con 239 expandidos contra 832.", { x: 0.6, y: 6.3, w: 12.1, h: 0.5, fontSize: 14, color: C.text2, objectName: "pie-graficos" });
s.addNotes("BFS camina 60 pasos pero cruza barro y paga costo 120. Dijkstra y A* encuentran costo 62. DFS expande muy pocos nodos pero su camino cuesta 126.");

// ================================================================== 10. Escalado
s = newSlide("CONTENIDO", "Resultados");
s.addText("A* crece más despacio con el tamaño", { placeholder: "title" });
const ns = ["20", "40", "60", "80", "100"];
s.addChart(pres.charts.LINE, [
  { name: "BFS", labels: ns, values: [315, 1274, 2867, 5107, 7975] },
  { name: "DFS", labels: ns, values: [88, 308, 797, 874, 2489] },
  { name: "Dijkstra", labels: ns, values: [310, 1272, 2865, 5103, 7970] },
  { name: "A*", labels: ns, values: [114, 357, 876, 1178, 1740] },
], {
  x: 0.6, y: 1.55, w: 8.3, h: 4.75, chartColors: colores, lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 8,
  showLegend: true, legendPos: "b", legendFontSize: 14, legendColor: HEX.text1, legendFontFace: "+mn-lt",
  catAxisLabelFontSize: 13, catAxisLabelColor: HEX.text2, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelFontSize: 13, valAxisLabelColor: HEX.text2, valAxisLabelFontFace: "+mn-lt",
  showCatAxisTitle: true, catAxisTitle: "Tamaño del mapa (n × n)", catAxisTitleFontSize: 13, catAxisTitleColor: HEX.text2, catAxisTitleFontFace: "+mn-lt",
  showValAxisTitle: true, valAxisTitle: "Nodos expandidos", valAxisTitleFontSize: 13, valAxisTitleColor: HEX.text2, valAxisTitleFontFace: "+mn-lt",
  valGridLine: { color: HEX.grid, size: 0.75 }, catGridLine: { style: "none" },
});
card(s, 9.3, 1.55, 3.43, 4.75, "panel-escalado");
T(s, "1740", { x: 9.6, y: 1.8, w: 2.9, h: 1.0, fontSize: 56, bold: true, color: C.accent1, valign: "middle" });
T(s, "nodos con n = 100, contra 7970 de Dijkstra", { x: 9.6, y: 2.85, w: 2.9, h: 0.8, fontSize: 16 });
T(s, "6.0 ms", { x: 9.6, y: 3.85, w: 2.9, h: 0.9, fontSize: 44, bold: true, color: C.text2, valign: "middle" });
T(s, "contra 19.9 ms de Dijkstra", { x: 9.6, y: 4.8, w: 2.9, h: 0.6, fontSize: 16 });
T(s, "BFS y Dijkstra se superponen en el gráfico.", { x: 9.6, y: 5.55, w: 2.9, h: 0.5, fontSize: 12, color: C.text2 });
T(s, "Mapas n×n con 20 % de paredes y 10 % de barro; 10 a 12 mapas con solución por tamaño.", { x: 0.6, y: 6.4, w: 12.1, h: 0.4, fontSize: 12, color: C.text2, objectName: "pie-escalado" });
s.addNotes("Al crecer el mapa, BFS y Dijkstra expanden casi toda la región más cercana que la meta. A* se dirige hacia la meta y expande mucho menos. DFS expande poco, pero con caminos no óptimos.");

// ================================================================== 11. Heurísticas y validación
s = newSlide("CONTENIDO", "Resultados");
s.addText("A* es óptimo y la heurística importa", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Nodos expandidos", labels: ["Dijkstra (h = 0)", "A* euclidiana", "A* Manhattan"], values: [1271, 970, 404] }], {
  x: 0.6, y: 1.55, w: 6.9, h: 4.6, barDir: "col", chartColors: [HEX.Dijkstra, HEX["A*"], HEX["A*"]], barGapWidthPct: 55,
  showTitle: true, title: "Nodos expandidos (promedio, 30 mapas 40×40)", titleFontSize: 16, titleColor: HEX.text1, titleFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 14, dataLabelColor: HEX.text1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0",
  catAxisLabelFontSize: 14, catAxisLabelColor: HEX.text2, catAxisLabelFontFace: "+mn-lt",
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
});
[
  ["8 de 8", "pruebas automáticas pasan"],
  ["120", "mapas verificados contra networkx"],
  ["30 de 30", "mapas donde A* igualó el costo de Dijkstra"],
].forEach(([num, texto], i) => {
  const y = 1.6 + i * 1.5;
  card(s, 8.0, y, 4.73, 1.3, `tarjeta-validacion-${i + 1}`);
  T(s, num, { x: 8.3, y, w: 1.9, h: 1.3, fontSize: 30, bold: true, color: C.text1, valign: "middle" });
  T(s, texto, { x: 10.2, y, w: 2.35, h: 1.3, fontSize: 15, valign: "middle" });
});
s.addNotes("Validamos Dijkstra y A* contra el costo óptimo que calcula networkx en 120 mapas. Con ambas heurísticas A* devolvió siempre el costo óptimo; Manhattan expande mucho menos que la euclidiana.");

// ================================================================== 12. Conclusiones
pres.addSection({ title: "Cierre" });
s = newSlide("OSCURO", "Cierre");
s.addText("Conclusiones", { placeholder: "title" });
[
  "El terreno decide: con barro BFS minimiza pasos, no costo (120 contra 62).",
  "A* da el óptimo de Dijkstra con una fracción de los nodos (239 contra 832).",
  "DFS es rápido pero poco confiable: costo 216 contra 74 en el mapa aleatorio.",
].forEach((texto, i) => {
  const y = 1.7 + i * 1.3;
  s.addText(String(i + 1), { x: 0.6, y, w: 0.7, h: 0.7, shape: pres.ShapeType.ellipse, fill: { color: C.accent1 }, color: C.background1, fontSize: 24, bold: true, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `numero-${i + 1}` });
  T(s, texto, { x: 1.6, y, w: 11.1, h: 0.7, fontSize: 24, color: C.background1, valign: "middle" });
});
T(s, "Demo en vivo · Preguntas", { x: 0.6, y: 5.9, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: C.accent3, fontFace: "Cambria", valign: "middle", objectName: "cierre" });
s.addNotes("Cerrar con las tres conclusiones y pasar a la demo en vivo de la aplicación: ejecutar cada algoritmo sobre el terreno, editar el mapa y usar Comparar todos.");

// ------------------------------------------------------------------ guardar
(async () => {
  await pres.writeFile({ fileName: "/home/claude/pc4/PC4_Presentacion.pptx" });
  await applyTheme("/home/claude/pc4/PC4_Presentacion.pptx", THEME);
  console.log("ok");
})();
