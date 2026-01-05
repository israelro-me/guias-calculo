Quiero que generes una guía de estudio de Cálculo para bachillerato en un SOLO archivo Markdown llamado `guia.md`.

REGLAS OBLIGATORIAS (no las rompas)
1) Devuelve ÚNICAMENTE el contenido del archivo Markdown (sin explicaciones fuera del documento).
2) No incluyas ningún bloque de código Python.
3) Todas las ecuaciones en bloque deben usar LaTeX con \[ ... \]
4) Las ecuaciones en línea deben usar \( ... \)
5) Si incluyes una imagen con Markdown, debe ser exactamente así:
   ![Texto alternativo](graficas/fig1.png)
6) Cada gráfica debe declararse con una directiva HTML multilínea ANTES de la imagen, con este formato exacto:

<!-- plot
kind=func2d
file=graficas/fig1.png
expr=...
xmin=...
xmax=...
n=400
title=...
xlabel=x
ylabel=f(x)
-->

![Texto alternativo](graficas/fig1.png)

7) El valor de `file=` debe coincidir EXACTAMENTE con la ruta de la imagen.
8) En `expr=` usa sintaxis tipo Python/NumPy usando la variable `x`:
   - potencias con ** (ej. x**2)
   - funciones permitidas: sin, cos, tan, exp, log, sqrt, abs, pi
   - usa sqrt(...) para raíces
9) Evita intervalos que rompan el dominio (por ejemplo, si hay sqrt(x-3), entonces xmin debe ser >= 3).
10) Usa SIEMPRE n=400 en func2d.
11) Usa SIEMPRE xlabel=x y ylabel=f(x).
12) Incluye máximo 2 gráficas.

ESTRUCTURA EXACTA DEL DOCUMENTO
# Título de la guía

## 1) Objetivo
- 3 a 5 líneas: qué se aprenderá.

## 2) Explicación breve
- 2 a 4 párrafos claros y directos (nivel bachillerato).
- Incluye al menos 1 ecuación en LaTeX.

## 3) Fórmulas clave
- Lista de 3 a 6 fórmulas relevantes (en LaTeX).

## 4) Ejemplo resuelto
- 1 problema resuelto paso a paso, con LaTeX bien presentado.

## 5) Ejercicios (sin soluciones)
- 12 ejercicios, de fácil a medio, numerados.
- Incluye variedad: cálculo directo, interpretación, dominio/rango, y al menos 2 ejercicios tipo “aplica tu conocimiento”.

## 6) Gráfica(s)
- Inserta 1 o 2 gráficas con directivas `<!-- plot ... -->` como se indicó.
- Deben corresponder a funciones usadas en la explicación o en el ejemplo resuelto.

DATOS QUE DEBES USAR PARA ESTA GUÍA
Tema: {ESCRIBE_AQUI_EL_TEMA}
Nivel: {básico|intermedio}
Enfoque: {por ejemplo: “dominio y rango”, “límites”, “derivadas”, etc.}
Si quieres incluir una función específica para graficar, usa esta (si no, elige una adecuada al tema):
Función sugerida: {por ejemplo: f(x)=sqrt(x+4), o deja vacío}

RECORDATORIO FINAL
- No Python.
- Solo Markdown.
- Gráficas con directivas plot, con TODOS los parámetros (kind, file, expr, xmin, xmax, n=400, title, xlabel=x, ylabel=f(x)).
