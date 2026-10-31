"""Gráfico de barras de la pobreza ENAHO por área, sexo, grupo de edad o dominio.

Uso: uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area [--anio 2024]

Reglas fijas: pondera siempre, barras desde cero y ordenadas, un solo color,
valor escrito en cada barra, título con qué y cuándo, fuente al pie, PNG a 200 dpi.
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR = "#2b5c8a"
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
DOMINIOS = {
    1: "Costa norte", 2: "Costa centro", 3: "Costa sur", 4: "Sierra norte",
    5: "Sierra centro", 6: "Sierra sur", 7: "Selva", 8: "Lima Metropolitana",
}
EDADES = [(0, 14, "0-14"), (15, 29, "15-29"), (30, 44, "30-44"), (45, 59, "45-59"), (60, 200, "60+")]


def pobreza_hogar(base: pd.DataFrame, grupo: pd.Series) -> pd.Series:
    """Método INEI para variables del hogar: un registro por hogar, factor07 × mieperho."""
    hog = base.assign(g=grupo).drop_duplicates(LLAVES_HOGAR)
    w = hog["factor07"] * hog["mieperho"]
    return 100 * (w * hog["pobre"]).groupby(hog["g"]).sum() / w.groupby(hog["g"]).sum()


def pobreza_persona(base: pd.DataFrame, grupo: pd.Series) -> pd.Series:
    """Para características de la persona: facpob07."""
    w = base["facpob07"]
    return 100 * (w * base["pobre"]).groupby(grupo).sum() / w.groupby(grupo).sum()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--por", choices=["area", "sexo", "edad", "dominio"], required=True)
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--extrema", action="store_true", help="pobreza extrema en vez de total")
    parser.add_argument("--salida", type=Path, default=Path("figuras"))
    args = parser.parse_args()

    ruta = Path("salidas") / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    base = pd.read_parquet(ruta)
    if args.extrema:
        base["pobre"] = base["pobre_extremo"]

    if args.por == "area":
        valores = pobreza_hogar(base, base["urbano"].map({True: "Urbano", False: "Rural"}))
        factor, eje = "factor07 × mieperho", "Área"
    elif args.por == "dominio":
        valores = pobreza_hogar(base, base["dominio"].map(DOMINIOS))
        factor, eje = "factor07 × mieperho", "Dominio"
    elif args.por == "sexo":
        valores = pobreza_persona(base, base["sexo"])
        factor, eje = "facpob07", "Sexo"
    else:
        grupo = pd.cut(base["edad"], [a - 0.5 for a, _, _ in EDADES] + [200], labels=[e for *_, e in EDADES])
        valores = pobreza_persona(base, grupo)
        factor, eje = "facpob07", "Grupo de edad"

    # Edad conserva su orden natural; lo demás se ordena de mayor a menor
    if args.por != "edad":
        valores = valores.sort_values(ascending=False)

    tipo = "Pobreza extrema" if args.extrema else "Pobreza monetaria"
    fig, ax = plt.subplots(figsize=(7, 4.2))
    barras = ax.bar(valores.index.astype(str), valores.values, color=COLOR)
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in valores.values], padding=3, fontsize=10)
    ax.set_ylim(0, max(valores.max() * 1.2, 5))
    ax.set_ylabel("% de personas")
    ax.set_xlabel(eje)
    ax.set_title(f"{tipo} por {eje.lower()}, Perú {args.anio}", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    if len(valores) > 5:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {args.anio}. Ponderado con {factor}.", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    args.salida.mkdir(parents=True, exist_ok=True)
    sufijo = "_extrema" if args.extrema else ""
    destino = args.salida / f"pobreza{sufijo}_{args.por}_{args.anio}.png"
    fig.savefig(destino, dpi=200)
    print(f"{tipo} por {eje.lower()} ({args.anio}, ponderado con {factor}):")
    for k, v in valores.items():
        print(f"  {k}: {v:.1f} %")
    print(f"Figura guardada en {destino}")


if __name__ == "__main__":
    main()
