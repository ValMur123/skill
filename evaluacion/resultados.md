# Resultados de claude -p (2026-10-31)

## Pedido 1 · con skills: ¿Cuál fue la pobreza en Cusco en 2024?
- Skills activadas: limpiando-enaho
- Turnos: 10

En 2024, el **18.5 %** de la población de Cusco era pobre (18.54 % sin redondear). La pobreza extrema fue de **2.1 %**.

| Indicador (Cusco, 2024) | Valor |
|---|---|
| Pobreza total | 18.5 % |
| Pobreza extrema | 2.1 % |
| Población expandida | ≈ 1.41 millones |
| Muestra | 1,230 hogares; 3,777 personas |

- **Cómo se ponderó:** usé `factor07 × mieperho`, con un registro por hogar, que es como publica el INEI las cifras por departamento. Si se pondera por persona con `facpob07`, el resultado es el mismo: 18.54 %.
- **Validación:** la base se armó con el script de limpieza de la ENAHO y pasó todos los chequeos. La pobreza nacional sale 27.58 %, contra el 27.6 % oficial, y la extrema 5.50 %, contra el 5.5 % oficial.
- **Archivos:** la base quedó en `salidas/personas_2024.parquet` y el reporte de validación en `salidas/validacion.txt`.

Fuente: INEI, ENAHO 2024.

Archivos: salidas/personas_2024.parquet salidas/validacion.txt 

## Pedido 1 · sin skills: ¿Cuál fue la pobreza en Cusco en 2024?
- Skills activadas: ninguna
- Turnos: 7

Según la ENAHO 2024, la **pobreza monetaria en Cusco fue de 18,5 %** de la población.

| Indicador (2024) | Cusco | Perú |
|---|---|---|
| Pobreza total (extrema + no extrema) | **18,5 %** | 27,6 % |
| Pobreza extrema | **2,1 %** | — |

**Cómo lo calculé:**
- Usé el archivo `sumaria-2024-12g.dta` dentro de `datos/966-Modulo34.zip`, leyéndolo sin descomprimirlo.
- Tomé los hogares con ubigeo del departamento 08 (Cusco): 1.230 hogares en la muestra.
- Un hogar cuenta como pobre si `pobreza` vale 1 (extrema) o 2 (no extrema).
- Cada hogar pesa factor07 × mieperho, así que la tasa es sobre personas y no sobre hogares. Con ese peso, la población estimada de Cusco es de unos 1,41 millones.
- El 27,6 % nacional coincide con la cifra oficial que publicó el INEI para 2024, así que el método parece correcto.

El script está en `C:\Users\valer\AppData\Local\Temp\claude\C--Users-valer-enaho-eval-p1-sin\5cfbc6c2-9bd5-4f23-818b-876b7175014a\scratchpad\pobreza.py`. Al ejecutarlo con `uv run` se creó un entorno `.venv` en la carpeta del proyecto.

Archivos: 

## Pedido 2 · con skills: Grafica la pobreza urbana y rural
- Skills activadas: graficando-enaho, limpiando-enaho
- Turnos: 10

Hice el gráfico de pobreza monetaria urbana y rural: `figuras/pobreza_area_2024.png`.

**Pobreza monetaria por área, Perú 2024**
- **Rural:** 39.3 %
- **Urbano:** 24.8 %

En el área rural la pobreza es unos 14.5 puntos más alta que en la urbana.

Las cifras están ponderadas con `factor07 × mieperho`, con un registro por hogar, que es como las publica el INEI.

Antes de graficar tuve que armar la base de personas (`salidas/personas_2024.parquet`) a partir de los módulos 34 y 02. Pasó todos los controles: la pobreza nacional sale 27.58 %, frente al 27.6 % oficial.

Fuente: INEI, ENAHO 2024.

Archivos: figuras/pobreza_area_2024.png salidas/personas_2024.parquet salidas/validacion.txt 

## Pedido 2 · sin skills: Grafica la pobreza urbana y rural
- Skills activadas: ninguna
- Turnos: 10

Ya hice el gráfico de pobreza urbana y rural de 2024. Está en `C:\Users\valer\enaho-eval\p2_sin\pobreza_urbana_rural.png`.

| Área | Pobreza extrema | Pobreza no extrema | **Pobreza total** |
|---|---|---|---|
| Nacional | 5.5% | 22.1% | **27.6%** |
| Urbana | 3.1% | 21.7% | **24.8%** |
| Rural | 15.5% | 23.8% | **39.3%** |

Las cifras coinciden con las que publicó el INEI para 2024. La pobreza rural (39.3%) está unos 14.5 puntos por encima de la urbana (24.8%). La diferencia es mayor en la pobreza extrema: en zonas rurales es cinco veces la urbana (15.5% frente a 3.1%).

**Cómo lo calculé:**
- **Datos:** la Sumaria 2024 (`sumaria-2024.dta`), que el script lee directamente desde `datos/966-Modulo34.zip`.
- **Urbano y rural:** se definen con `estrato`, igual que lo hace el INEI. Los estratos 1 a 5 cuentan como urbanos y los 6 a 8 como rurales.
- **Ponderación:** cada hogar pesa su factor de expansión (`factor07`) multiplicado por el número de miembros (`mieperho`). Así las tasas se refieren a personas y no a hogares.

El código está en `graficar_pobreza_area.py` y se ejecuta con `uv run python graficar_pobreza_area.py`. Si quieres, puedo separar el gráfico por región natural (costa, sierra, selva) o hacer un mapa por departamento con el geojson que tienes en `datos/`.

Archivos: graficar_pobreza_area.py pobreza_urbana_rural.png 

## Pedido 3 · con skills: Haz un mapa de la pobreza por departamento con la ENAHO 2024
- Skills activadas: mapeando-enaho, limpiando-enaho
- Turnos: 10

El mapa está en `mapas/pobreza_departamento.png`. Pasó todos los controles: hay 25 departamentos con dato, Lima y Callao van separados, y el script unió los datos por código de ubigeo, no por nombre.

**Más pobreza**
1. Cajamarca: 45.0 %
2. Loreto: 43.0 %
3. Puno: 39.9 %

**Menos pobreza**
1. Ica: 6.0 %
2. Moquegua: 11.0 %
3. Madre de Dios: 11.1 %

Las seis cifras son iguales a los valores de control del INEI para 2024. La pobreza nacional sale 27.58 %, frente al 27.6 % oficial.

**Ponderación:** usé el método del INEI, con un registro por hogar ponderado por `factor07 × mieperho`.

La base de personas no existía, así que antes generé y validé `salidas/personas_2024.parquet` (108,664 personas en 33,691 hogares).

El mapa tiene una escala de un solo azul que va de 0 a 50 %, y la leyenda está en % de personas en pobreza monetaria.

Fuente: INEI, ENAHO 2024.

Archivos: mapas/pobreza_departamento.png mapas/pobreza_departamento_2024.csv salidas/personas_2024.parquet salidas/validacion.txt 

## Pedido 3 · sin skills: Haz un mapa de la pobreza por departamento con la ENAHO 2024
- Skills activadas: ninguna
- Turnos: 15

Hice el mapa con la ENAHO 2024. La pobreza a nivel nacional sale **27,6 %** y la extrema **5,5 %**, que son las mismas cifras que publicó el INEI para 2024.

![mapa](resultados/mapa_pobreza_departamental_2024.png)

**Archivos generados**
- `resultados/mapa_pobreza_departamental_2024.png`: el mapa.
- `resultados/pobreza_departamental_2024.csv`: tabla con la pobreza total y la extrema por departamento, la población expandida y cuántos hogares hay en la muestra de cada uno.
- `mapa_pobreza.py`: script para volver a generar todo con `uv run python mapa_pobreza.py`. Lee el `.dta` directamente desde el zip, sin descomprimirlo.

**Cómo se calculó**
- Usé la base Sumaria (módulo 34). Una persona cuenta como pobre si la variable `pobreza` vale 1 (pobre extremo) o 2 (pobre no extremo).
- La tasa es por personas, no por hogares. Cada hogar se pondera por `factor07 × mieperho`.
- El departamento se toma de los dos primeros dígitos de `ubigeo`.

**Resultados**
- **Más pobreza:** Cajamarca (45,0 %), Loreto (43,0 %), Puno (39,9 %), Pasco y Huánuco (39,0 % cada uno).
- **Menos pobreza:** Ica (6,0 %), Moquegua (11,0 %), Madre de Dios (11,1 %) y Lambayeque (14,0 %).

**Antes de usarlo**
- **Lima** (27,1 %) suma Lima Metropolitana y Lima Provincias, porque el geojson trae un solo polígono. Callao (33,9 %) va aparte. El INEI suele reportar "Lima Metropolitana" incluyendo al Callao, así que esa cifra no se compara directamente con esta.
- Son **estimaciones puntuales, sin intervalos de confianza**. Algunos departamentos tienen muestras chicas (Madre de Dios tiene 603 hogares), y por eso el INEI publica los resultados departamentales en grupos de pobreza estadísticamente parecida. Para ordenar departamentos con valores cercanos, como Pasco y Huánuco, conviene calcular los intervalos teniendo en cuenta el diseño muestral (conglomerado y estrato).

¿Quieres que agregue un segundo mapa de pobreza extrema o que calcule los intervalos de confianza?

Archivos: mapa_pobreza.py resultados/mapa_pobreza_departamental_2024.png resultados/pobreza_departamental_2024.csv 
