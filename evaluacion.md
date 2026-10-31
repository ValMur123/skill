# Evaluación: tres pedidos con y sin skills

Cada pedido se corrió con `claude -p` (Claude Code 2.1.316) en una copia limpia del repo, **sin `salidas/`**, para
probar que las skills de gráficos y mapas activan primero `limpiando-enaho`. En «sin skills» la copia no lleva
`.claude/` y además se usa `--disallowedTools Skill`, para que Claude no pueda leer ni correr los scripts de las skills.

```bash
bash evaluacion/evaluar.sh      # escribe evaluacion/resultados.md con la respuesta completa de cada corrida
```

| # | Pedido | Modo | Skills que se activaron | Cifra | ¿Ponderó? | Figura | Esperado |
|---|---|---|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | con | `limpiando-enaho` | 18.5 % | Sí, `factor07 × mieperho` (y comprobó `facpob07`: 18.54 %) | — | 18.5 % |
| 1 | | sin | — | 18.5 % | Sí, `factor07 × mieperho` | — (script suelto en una carpeta temporal) | 18.5 % |
| 2 | Grafica la pobreza urbana y rural | con | `graficando-enaho` → `limpiando-enaho` | 24.8 % y 39.3 % | Sí, `factor07 × mieperho` por hogar | `figuras/pobreza_area_2024.png`: un color, desde 0, ordenada, con fuente | 24.8 % y 39.3 % |
| 2 | | sin | — | 24.8 % y 39.3 % | Sí, `factor07 × mieperho` | [`sin_skills_grafico_area.png`](evaluacion/sin_skills_grafico_area.png): barras apiladas de dos colores, agrega «Nacional», archivo en la raíz | 24.8 % y 39.3 % |
| 3 | Haz un mapa de la pobreza por departamento con la ENAHO 2024 | con | `mapeando-enaho` → `limpiando-enaho` | Cajamarca 45.0 %, Ica 6.0 % | Sí, `factor07 × mieperho` | `mapas/pobreza_departamento.png`: `Blues` de 0 a 50 %, 25 departamentos, unión por código | Cajamarca 45.0 %, Ica 6.0 % |
| 3 | | sin | — | Cajamarca 45.0 %, Ica 6.0 % | Sí, `factor07 × mieperho` | [`sin_skills_mapa.png`](evaluacion/sin_skills_mapa.png): `OrRd` que empieza en 6 %, no en 0; carpeta `resultados/` | Cajamarca 45.0 %, Ica 6.0 % |

## Qué se observó

- **Las skills se activan solas.** Ningún pedido nombró una skill y las tres se usaron cuando correspondía.
- **Encadenamiento.** Los pedidos 2 y 3 activaron dos skills seguidas: como no existía
  `salidas/personas_2024.parquet`, `graficando-enaho` y `mapeando-enaho` llamaron primero a `limpiando-enaho`.
- **Sin skills, Claude también llegó a las cifras correctas.** Calculó directo de la sumaria con `factor07 × mieperho`
  y unió el mapa por código. Con la ENAHO 2024 y un pedido simple, Claude ya sabe ponderar. La diferencia no está en
  la cifra sino en todo lo demás:
  - **No hay base de personas ni validación.** Sin skills nunca filtró residentes habituales ni unió los módulos 34 y
    02, y no dejó `validacion.txt`. Para preguntas por sexo o edad no tendría una base de dónde partir.
  - **Cada corrida inventa su propio formato.** El script queda en un lugar distinto cada vez (carpeta temporal, raíz,
    `resultados/`), con otro nombre y otro diseño: barras apiladas en dos rojos en el pedido 2, escala `OrRd` desde 6 %
    en el mapa. Con skills, las tres corridas dejan los mismos archivos, en las mismas carpetas y con las mismas reglas.
  - **La escala del mapa sin skills no empieza en 0.** Ica (6 %) sale casi blanca, como si no tuviera pobreza; la regla
    «un color de claro a oscuro, desde 0» de `mapeando-enaho` lo evita.
- **Costo parecido.** Con skills se usaron 10 turnos por pedido; sin skills, entre 7 y 15.
