# Evaluación: tres pedidos con y sin skills

Cada pedido se corrió con `claude -p` en una copia limpia del repo, sin `salidas/`, para probar que las skills de
gráficos y mapas activan primero `limpiando-enaho`. «Sin skills» usa `--disallowedTools Skill`.

```bash
bash evaluacion/evaluar.sh      # escribe evaluacion/resultados.md con el detalle de cada corrida
```

| # | Pedido | Modo | Skills que se activaron | Cifra | ¿Ponderó? | Figura | Esperado |
|---|---|---|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | con | | | | — | 18.5 % |
| 1 | | sin | — | | | — | 18.5 % |
| 2 | Grafica la pobreza urbana y rural | con | | | | | 24.8 % y 39.3 % |
| 2 | | sin | — | | | | 24.8 % y 39.3 % |
| 3 | Haz un mapa de la pobreza por departamento con la ENAHO 2024 | con | | | | | Cajamarca 45.0 %, Ica 6.0 % |
| 3 | | sin | — | | | | Cajamarca 45.0 %, Ica 6.0 % |

## Qué se observó

<!-- Completar con evaluacion/resultados.md: ¿se encadenaron dos skills? ¿sin skills unió por nombre, usó arcoíris,
contó encuestas en vez de ponderar, o filtró distinto a los residentes? -->
