#!/usr/bin/env bash
# Corre los tres pedidos con y sin skills, cada uno en una copia limpia del repo (sin salidas/),
# y guarda en evaluacion/resultados.md qué skills se activaron y qué respondió Claude.
# Uso (desde la raíz del repo, en Git Bash): bash evaluacion/evaluar.sh
set -u
export PYTHONIOENCODING=utf-8   # sin esto, Windows falla al escribir tildes y símbolos en resultados.md
RAIZ="$PWD"
TMP="${TMPDIR:-$HOME}/enaho-eval"   # ruta corta: Windows falla con rutas de más de 260 caracteres
PEDIDOS=(
  "¿Cuál fue la pobreza en Cusco en 2024?"
  "Grafica la pobreza urbana y rural"
  "Haz un mapa de la pobreza por departamento con la ENAHO 2024"
)
SALIDA="$RAIZ/evaluacion/resultados.md"
echo "# Resultados de claude -p ($(date +%F))" > "$SALIDA"
rm -rf "$TMP"; mkdir -p "$TMP"
for i in 0 1 2; do
  for modo in con sin; do
    d="$TMP/p$((i+1))_$modo"; mkdir -p "$d"
    cp -r datos pyproject.toml uv.lock .python-version "$d/"
    # Sin skills: además de bloquear la herramienta Skill, la copia no lleva .claude/,
    # para que Claude no lea ni corra los scripts de las skills por su cuenta
    extra=(--disallowedTools Skill)
    [ "$modo" = con ] && { cp -r .claude "$d/"; extra=(); }
    (cd "$d" && git init -q && claude -p "${PEDIDOS[$i]}" --output-format stream-json --verbose --max-turns 40 \
      --allowedTools Skill Read Write Edit Glob Grep "Bash(uv:*)" "Bash(ls:*)" "PowerShell(uv:*)" \
      "${extra[@]}" > log.jsonl 2>&1) &
  done
done
wait
for i in 0 1 2; do
  for modo in con sin; do
    d="$TMP/p$((i+1))_$modo"
    { echo; echo "## Pedido $((i+1)) · $modo skills: ${PEDIDOS[$i]}"; python - "$d/log.jsonl" <<'PY'
import json, sys
skills, res = [], None
for linea in open(sys.argv[1], encoding="utf-8"):
    try:
        e = json.loads(linea)
    except ValueError:
        continue
    if e.get("type") == "assistant":
        skills += [c["input"].get("skill") for c in e["message"].get("content", [])
                   if c.get("type") == "tool_use" and c["name"] == "Skill"]
    if e.get("type") == "result":
        res = e
print(f"- Skills activadas: {', '.join(skills) or 'ninguna'}")
print(f"- Turnos: {res.get('num_turns') if res else '?'}")
print("\n" + ((res or {}).get("result") or "(sin respuesta)").strip())
PY
      echo; echo "Archivos: $(cd "$d" && find figuras mapas salidas -type f 2>/dev/null | tr '\n' ' ')"; } >> "$SALIDA"
  done
done
echo "Listo: $SALIDA (las figuras de cada corrida quedan en $TMP)"
