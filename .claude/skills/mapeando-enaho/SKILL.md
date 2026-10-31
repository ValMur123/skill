---
name: mapeando-enaho
description: Hace un mapa de la pobreza de la ENAHO del INEI por departamento del Perú, uniendo por código de ubigeo con los límites departamentales y validando los 25 departamentos. Úsala cuando pidan un mapa, coroplético o la pobreza por departamento o región en un mapa.
argument-hint: [año]
---

# Mapear la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
2. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py`
   El script baja el GeoJSON a `datos/` si falta.
3. Si un assert falla, detente y di cuál: no dibujes el mapa por otra vía.
4. Responde con `mapas/pobreza_departamento.png`, los tres departamentos con más y menos pobreza
   y el factor con que se ponderó.

## Reglas que no se discuten (ya están en el script)

- Une por código: `ubigeo[:2]` con `FIRST_IDDP`, los dos como texto con cero a la izquierda.
- Nunca por nombre: «APURIMAC» no es «Apurímac».
- Exige 25 departamentos y ninguno sin dato.
- Lima (15) y Callao (07) van separados.
- Pondera con el método INEI: un registro por hogar y `factor07 × mieperho`.
- Un solo color de claro a oscuro (`Blues`), desde 0; nunca arcoíris.
- Leyenda con la unidad: % de personas. Fuente al pie: «Fuente: INEI, ENAHO 2024».
- Control 2024: Cajamarca 45.0 %, Loreto 43.0 %, Puno 39.9 %, Ica 6.0 %, Moquegua 11.0 %, Madre de Dios 11.1 %.
