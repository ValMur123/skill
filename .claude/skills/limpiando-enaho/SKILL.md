---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas con pobreza, departamento, área, sexo, edad y factor de expansión, validada contra la pobreza oficial. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular la pobreza nacional, por región, departamento, área, sexo o edad.
argument-hint: [año]
---

# Limpiar la ENAHO

1. Si ya existen `salidas/personas_$0.parquet` y `salidas/validacion.txt` con `RESULTADO: VALIDADO`, sáltate el paso 3.
   Si no se pasó año, usa 2024.
2. Si faltan `datos/966-Modulo34.zip` o `datos/966-Modulo02.zip`, pide al usuario bajarlos del INEI
   (código 966 = 2024; los links están en `reference.md`). No inventes datos.
3. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0`
   No reescribas la limpieza ni la hagas a mano: el script fija las llaves, el filtro, la unión y la validación.
4. Lee `salidas/validacion.txt`. Si dice `NO VALIDADO` o la pobreza difiere del INEI en más de 0.1 puntos,
   detente y muéstrale al usuario qué chequeo falló.
5. Responde con `salidas/personas_$0.parquet`. Toda cifra va ponderada:
   - Por persona (sexo, edad, parentesco): `facpob07`.
   - Cifras oficiales por departamento, área o nacional: `factor07 × mieperho` sobre un registro por hogar,
     como publica el INEI. Así Cusco da 18.5 %.
   - `pobre` es `pobreza <= 2`; nunca promedies el código `pobreza`.
6. Antes de usar una variable que no está en la base, lee `reference.md`.
7. Al dar una cifra, di con qué factor se ponderó y cita «Fuente: INEI, ENAHO 2024».
