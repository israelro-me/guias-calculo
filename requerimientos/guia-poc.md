# Función racional y notación de cálculo

En esta guía mínima probaremos que se rendericen correctamente expresiones de cálculo como fracciones, límites, derivadas e integrales, y además graficaremos una función racional.

La función que analizaremos es:

\[
f(x) = \frac{x}{x^2 + 1}
\]

Esta función es **impar**, ya que se cumple:

\[
f(-x) = \frac{-x}{(-x)^2 + 1} = \frac{-x}{x^2 + 1} = -f(x).
\]

## Derivada de la función

Aplicando la regla del cociente, con \(u(x) = x\) y \(v(x) = x^2 + 1\):

\[
f'(x) = \frac{u'(x)v(x) - u(x)v'(x)}{[v(x)]^2}
      = \frac{1\cdot(x^2+1) - x\cdot(2x)}{(x^2+1)^2}
      = \frac{1 - x^2}{(x^2+1)^2}.
\]

Los puntos donde la derivada se anula satisfacen:

\[
1 - x^2 = 0 \quad \Rightarrow \quad x^2 = 1 \quad \Rightarrow \quad x = -1,\; 1.
\]

## Límites

Como el denominador crece más rápido que el numerador, tenemos:

\[
\lim_{x \to \infty} \frac{x}{x^2 + 1} = 0,
\qquad
\lim_{x \to -\infty} \frac{x}{x^2 + 1} = 0.
\]

Esto indica que el eje \(x\) es una **asíntota horizontal**.

## Integral definida

El integrando es una función impar, por lo que la integral en un intervalo simétrico alrededor de 0 se anula:

\[
\int_{-1}^{1} \frac{x}{x^2 + 1}\,dx = 0.
\]

De hecho, una primitiva es:

\[
\int \frac{x}{x^2 + 1}\,dx = \tfrac{1}{2}\ln(x^2+1) + C.
\]

## Gráfica de la función

A continuación se muestra la gráfica de \( f(x) = \frac{x}{x^2 + 1} \) en el intervalo \([-5, 5]\). Observa que la curva es simétrica respecto al origen, se aproxima al eje \(x\) cuando \(|x|\) es grande y tiene un máximo local cerca de \(x \approx 0.577\) y un mínimo local cerca de \(x \approx -0.577\).

### Gráfica de \( f(x) = \frac{x}{x^2 + 1} \)

![](graficas\racional1.png)
