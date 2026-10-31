---
name: graficando-enaho
description: Grafica la pobreza de la ENAHO del INEI en barras por área urbana y rural, sexo, grupo de edad o dominio, ponderada con el factor de expansión y con reglas fijas de diseño. Úsala cuando pidan un gráfico, figura, barras o visualización de la pobreza o de la ENAHO.
argument-hint: [area|sexo|edad|dominio]
---

# Graficar la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
2. Elige `--por` según el pedido: `area` (urbano/rural), `sexo`, `edad` o `dominio`. Si se pasó argumento, usa `$0`.
   Para pobreza extrema agrega `--extrema`.
3. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por <grupo>`
4. Responde con la ruta del PNG en `figuras/` y las cifras que imprimió el script, diciendo con qué factor se ponderó.

## Reglas que no se discuten (ya están en el script)

- Pondera siempre: `facpob07` para sexo y edad; `factor07 × mieperho` por hogar para área y dominio (método INEI).
- Barras que empiezan en cero y ordenadas de mayor a menor (la edad conserva su orden).
- Un solo color y el valor escrito en cada barra.
- El título dice qué y cuándo: «Pobreza monetaria por área, Perú 2024».
- Nota al pie: «Fuente: INEI, ENAHO 2024».
- PNG a 200 dpi en `figuras/`.

Si piden un gráfico que el script no cubre, agrégalo al script respetando estas mismas reglas; no lo hagas aparte.
Si piden un mapa por departamento, usa la skill `mapeando-enaho`.
