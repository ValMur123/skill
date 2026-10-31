"""Mapa coroplético de la pobreza ENAHO por departamento.

Uso: uv run .claude/skills/mapeando-enaho/scripts/mapear.py [--anio 2024]

Une por código (ubigeo[:2] con FIRST_IDDP, como texto), nunca por nombre.
Exige 25 departamentos con dato y valida contra las cifras del INEI.
"""

import argparse
import sys
import urllib.request
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GEOJSON = Path("datos/peru_departamental_simple.geojson")
GEOJSON_URL = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
# Cifras de control 2024 (sumaria, factor07 × mieperho)
CONTROL = {2024: {"06": 45.0, "16": 43.0, "21": 39.9, "11": 6.0, "18": 11.0, "17": 11.1}}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--salida", type=Path, default=Path("mapas"))
    args = parser.parse_args()

    ruta = Path("salidas") / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    if not GEOJSON.exists():
        GEOJSON.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(GEOJSON_URL, GEOJSON)

    # Pobreza por departamento con el método INEI: un registro por hogar, factor07 × mieperho
    base = pd.read_parquet(ruta)
    hog = base.drop_duplicates(LLAVES_HOGAR)
    w = hog["factor07"] * hog["mieperho"]
    pobreza = (100 * (w * hog["pobre"]).groupby(hog["departamento"]).sum() / w.groupby(hog["departamento"]).sum())
    pobreza = pobreza.rename("pobreza").reset_index()
    pobreza["departamento"] = pobreza["departamento"].astype(str).str.zfill(2)

    # Unión por código, como texto; Lima (15) y Callao (07) quedan separados
    geo = gpd.read_file(GEOJSON)
    geo["FIRST_IDDP"] = geo["FIRST_IDDP"].astype(str).str.zfill(2)
    mapa = geo.merge(pobreza, left_on="FIRST_IDDP", right_on="departamento", how="left", validate="1:1")

    assert len(mapa) == 25, f"Se esperaban 25 departamentos, hay {len(mapa)}"
    sin_dato = mapa.loc[mapa["pobreza"].isna(), "NOMBDEP"].tolist()
    assert not sin_dato, f"Departamentos sin dato (revisa la unión): {sin_dato}"
    for cod, ref in CONTROL.get(args.anio, {}).items():
        valor = mapa.loc[mapa["FIRST_IDDP"] == cod, "pobreza"].item()
        assert abs(valor - ref) < 0.1, f"{cod}: {valor:.2f} % vs INEI {ref} %"

    # Un solo tono de claro a oscuro, desde 0
    fig, ax = plt.subplots(figsize=(7, 9))
    mapa.plot(
        column="pobreza", cmap="Blues", vmin=0, vmax=50, ax=ax, edgecolor="white", linewidth=0.6,
        legend=True, legend_kwds={"label": "% de personas en pobreza monetaria", "shrink": 0.6},
    )
    for _, fila in mapa.iterrows():
        p = fila.geometry.representative_point()
        if fila["FIRST_IDDP"] == "07":
            # Callao es muy pequeño: etiqueta afuera, en el mar
            ax.annotate(f"Callao {fila['pobreza']:.1f}", (p.x, p.y), xytext=(p.x - 2.2, p.y), ha="center",
                        va="center", fontsize=7, color="#222", arrowprops={"arrowstyle": "-", "color": "#555", "lw": 0.6})
            continue
        color = "white" if fila["pobreza"] > 30 else "#222"
        ax.annotate(f"{fila['pobreza']:.1f}", (p.x, p.y), ha="center", va="center", fontsize=7, color=color)
    ax.set_title(f"Pobreza monetaria por departamento, Perú {args.anio}", loc="left", fontweight="bold")
    ax.set_axis_off()
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {args.anio}. Ponderado con factor07 × mieperho.", fontsize=8, color="#555")

    args.salida.mkdir(parents=True, exist_ok=True)
    destino = args.salida / "pobreza_departamento.png"
    fig.savefig(destino, dpi=200, bbox_inches="tight")
    pobreza.to_csv(args.salida / f"pobreza_departamento_{args.anio}.csv", index=False, float_format="%.2f")

    orden = mapa.sort_values("pobreza", ascending=False)
    print(f"Pobreza por departamento ({args.anio}, factor07 × mieperho), 25 con dato:")
    for _, fila in orden.iterrows():
        print(f"  {fila['FIRST_IDDP']} {fila['NOMBDEP']}: {fila['pobreza']:.1f} %")
    print(f"Mapa guardado en {destino}")


if __name__ == "__main__":
    main()
