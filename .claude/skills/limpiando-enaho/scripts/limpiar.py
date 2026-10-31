"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO y arma una base de personas.

Uso: uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024

Pipeline, siempre en este orden:
1. Leer los .dta sin convertir etiquetas; llaves como texto.
2. Normalizar nombres de columna (minúscula; «aÑo» -> anio).
3. Filtrar residentes habituales.
4. Unir personas con su hogar (validate="m:1").
5. Construir departamento, urbano, pobre, pobre_extremo.
6. Validar llaves, filas y pobreza oficial.
7. Guardar salidas/personas_<anio>.parquet y salidas/validacion.txt.
"""

import argparse
import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

# Código del INEI en el portal de microdatos y cifras oficiales para validar
CODIGOS = {2024: 966}
OFICIAL = {2024: {"pobreza": 27.6, "extrema": 5.5, "residentes": 108_664, "hogares": 33_691}}
TOLERANCIA = 0.1  # puntos porcentuales

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]

COLS_SUMARIA = LLAVES_HOGAR + [
    "ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07",
    "gashog2d", "inghog2d", "linea", "linpe",
]
COLS_MIEMBROS = LLAVES_PERSONA + ["p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]


def normalizar(nombre: str) -> str:
    """«aÑo» -> «anio»; quita tildes y pasa a minúscula."""
    nombre = nombre.strip().lower().replace("ñ", "ni")
    return unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()


def leer_dta(zip_path: Path, patron: str, columnas: list[str], llaves: list[str]) -> pd.DataFrame:
    """Paso 1 y 2: lee el .dta dentro del zip, normaliza nombres y deja las llaves como texto."""
    if not zip_path.exists():
        sys.exit(f"Falta {zip_path}. Bájalo del INEI y ponlo en datos/.")
    with zipfile.ZipFile(zip_path) as z:
        nombre = next(n for n in z.namelist() if n.lower().endswith(patron))
        df = pd.read_stata(io.BytesIO(z.read(nombre)), convert_categoricals=False)
    df.columns = [normalizar(c) for c in df.columns]
    df = df[[c for c in columnas if c in df.columns]].copy()
    for c in llaves + ["ubigeo"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    # Los ceros a la izquierda no se pierden: se rellenan por si vinieran como número
    if "ubigeo" in df.columns:
        df["ubigeo"] = df["ubigeo"].str.zfill(6)
    return df


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--datos", type=Path, default=Path("datos"))
    parser.add_argument("--salidas", type=Path, default=Path("salidas"))
    args = parser.parse_args()

    anio = args.anio
    if anio not in CODIGOS:
        sys.exit(f"Año {anio} no configurado. Agrega su código del INEI en CODIGOS.")
    cod = CODIGOS[anio]
    oficial = OFICIAL[anio]
    args.salidas.mkdir(parents=True, exist_ok=True)

    # 1-2. Leer y normalizar
    sumaria = leer_dta(args.datos / f"{cod}-Modulo34.zip", f"sumaria-{anio}.dta", COLS_SUMARIA, LLAVES_HOGAR)
    miembros = leer_dta(args.datos / f"{cod}-Modulo02.zip", f"enaho01-{anio}-200.dta", COLS_MIEMBROS, LLAVES_PERSONA)
    n_miembros = len(miembros)

    # 3. Filtrar residentes habituales (definición del INEI)
    residente = ((miembros.p204 == 1) & (miembros.p205 == 2)) | ((miembros.p204 == 2) & (miembros.p206 == 1))
    personas = miembros[residente].copy()

    # 4. Unir personas con su hogar; falla si un hogar se repite
    base = personas.merge(sumaria, on=LLAVES_HOGAR, how="left", validate="m:1", indicator=True)

    # 5. Construir variables
    base["anio"] = anio
    base["departamento"] = base["ubigeo"].str[:2]
    base["urbano"] = base["estrato"] <= 5
    base["pobre"] = base["pobreza"] <= 2
    base["pobre_extremo"] = base["pobreza"] == 1
    base["sexo"] = base["p207"].map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base["p208a"]

    # 6. Validar
    sin_hogar = int((base["_merge"] != "both").sum())
    base = base.drop(columns="_merge")

    w_hog = sumaria["factor07"] * sumaria["mieperho"]
    pob_sumaria = 100 * (w_hog * (sumaria["pobreza"] <= 2)).sum() / w_hog.sum()
    ext_sumaria = 100 * (w_hog * (sumaria["pobreza"] == 1)).sum() / w_hog.sum()
    pob_personas = 100 * (base["facpob07"] * base["pobre"]).sum() / base["facpob07"].sum()
    poblacion = base["facpob07"].sum()

    chequeos = [
        ("Llaves de hogar únicas en la sumaria", not sumaria.duplicated(LLAVES_HOGAR).any()),
        ("Llaves de persona únicas", not personas.duplicated(LLAVES_PERSONA).any()),
        ("La unión no perdió ni duplicó filas", len(base) == len(personas)),
        ("Todas las personas tienen hogar en la sumaria", sin_hogar == 0),
        (f"Hogares = {oficial['hogares']:,}", len(sumaria) == oficial["hogares"]),
        (f"Residentes habituales = {oficial['residentes']:,}", len(base) == oficial["residentes"]),
        (f"Pobreza a {TOLERANCIA} pts de {oficial['pobreza']} %", abs(pob_sumaria - oficial["pobreza"]) < TOLERANCIA),
        (f"Pobreza extrema a {TOLERANCIA} pts de {oficial['extrema']} %", abs(ext_sumaria - oficial["extrema"]) < TOLERANCIA),
        ("25 departamentos", base["departamento"].nunique() == 25),
    ]
    ok = all(c for _, c in chequeos)

    lineas = [
        f"Validación ENAHO {anio} · módulos 34 y 02 (código INEI {cod})",
        "",
        f"Filas módulo 02:            {n_miembros:,}",
        f"Residentes habituales:      {len(base):,}",
        f"Hogares en la sumaria:      {len(sumaria):,}",
        f"Población expandida:        {poblacion:,.0f}",
        "",
        f"Pobreza (sumaria, factor07 x mieperho):  {pob_sumaria:.2f} %   oficial INEI: {oficial['pobreza']} %",
        f"Pobreza extrema (sumaria):               {ext_sumaria:.2f} %   oficial INEI: {oficial['extrema']} %",
        f"Pobreza (personas, facpob07):            {pob_personas:.2f} %",
        "",
        *[f"[{'OK' if c else 'FALLA'}] {texto}" for texto, c in chequeos],
        "",
        f"RESULTADO: {'VALIDADO' if ok else 'NO VALIDADO: no uses esta base'}",
    ]
    texto = "\n".join(lineas) + "\n"
    (args.salidas / "validacion.txt").write_text(texto, encoding="utf-8")
    print(texto)

    # 7. Guardar
    salida = args.salidas / f"personas_{anio}.parquet"
    base.to_parquet(salida, index=False)
    print(f"Base guardada en {salida} ({len(base):,} filas, {base.shape[1]} columnas)")

    # Asserts al final, como pide la validación
    assert not personas.duplicated(LLAVES_PERSONA).any()
    assert len(base) == len(personas)  # la unión no perdió ni duplicó filas
    assert abs(pob_sumaria - oficial["pobreza"]) < TOLERANCIA  # cifra oficial del INEI
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
