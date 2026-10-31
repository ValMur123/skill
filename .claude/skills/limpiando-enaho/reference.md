# Referencia ENAHO 2024

## Descarga

| Módulo | Link | Archivo dentro del zip |
|---|---|---|
| 34 · Sumaria | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip | `sumaria-2024.dta` |
| 02 · Miembros | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip | `enaho01-2024-200.dta` |

Los zip van tal cual en `datos/` (el script los lee sin descomprimir). `datos/` no se sube a git.

## Columnas de `salidas/personas_2024.parquet`

Una fila por residente habitual (108,664).

| Columna | Origen | Significado |
|---|---|---|
| `conglome`, `vivienda`, `hogar`, `codperso` | 02 | Llaves, como texto (conservan ceros: «015009») |
| `p203` | 02 | Parentesco con el jefe (1 jefe, 2 cónyuge, 3 hijo, …) |
| `p204`, `p205`, `p206` | 02 | Miembro del hogar, ausente 30+ días, presente 30+ días |
| `p207` / `sexo` | 02 | 1 Hombre, 2 Mujer |
| `p208a` / `edad` | 02 | Edad en años |
| `facpob07` | 02 | Factor de expansión de personas |
| `ubigeo` | 34 | Código de 6 dígitos, texto |
| `departamento` | derivada | `ubigeo[:2]`, texto «01»…«25». Lima es 15 y Callao 07 |
| `dominio` | 34 | 1–7 costa/sierra/selva norte, centro, sur; 8 Lima Metropolitana |
| `estrato` | 34 | 1–5 urbano, 6–8 rural |
| `urbano` | derivada | `estrato <= 5` |
| `pobreza` | 34 | 1 pobre extremo, 2 pobre no extremo, 3 no pobre (código, no número) |
| `pobre`, `pobre_extremo` | derivadas | `pobreza <= 2`, `pobreza == 1` |
| `mieperho` | 34 | Miembros del hogar |
| `factor07` | 34 | Factor de expansión del hogar |
| `gashog2d`, `inghog2d` | 34 | Gasto e ingreso anual del hogar (soles) |
| `linea`, `linpe` | 34 | Línea de pobreza y de pobreza extrema (mensual per cápita) |

Gasto per cápita mensual: `gashog2d / (12 * mieperho)`.

## Cómo ponderar

- Cifra oficial (nacional, departamento, área, dominio): toma un registro por hogar
  (`drop_duplicates(["conglome","vivienda","hogar"])`) y pondera con `factor07 * mieperho`.
- Cifra por características de la persona (sexo, edad): pondera con `facpob07`.
- Nunca cuentes encuestas: 33,691 hogares representan 34.1 millones de personas.

## Cifras de control 2024

| Cifra | Valor |
|---|---|
| Pobreza nacional | 27.6 % (27.58 % sumaria; 27.53 % personas con `facpob07`) |
| Pobreza extrema | 5.5 % |
| Urbano / rural | 24.8 % / 39.3 % |
| Lima Metropolitana (`dominio == 8`) | 28.2 % |
| Cusco | 18.5 % |
| Cajamarca / Ica | 45.0 % / 6.0 % |

## Variables que no están en la base

Otras variables del módulo 02 (p. ej. `p209` estado civil) o de la sumaria (p. ej. `percepho`):
agrégalas a `COLS_MIEMBROS` o `COLS_SUMARIA` en `scripts/limpiar.py`, vuelve a correrlo y
revisa que la validación siga en `VALIDADO`. Educación y empleo están en otros módulos (03, 05).
