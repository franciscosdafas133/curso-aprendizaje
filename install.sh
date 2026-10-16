#!/usr/bin/env bash
# Instalador del plugin curso-aprendizaje (Cursor y/o Claude Code)
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/franciscosdafas133/curso-aprendizaje.git}"
TARGET="${1:-all}"   # cursor | claude | all
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== clonando $REPO_URL =="
git clone --depth 1 "$REPO_URL" "$TMP/curso-aprendizaje"
ROOT="$TMP/curso-aprendizaje"

install_cursor() {
  mkdir -p "${HOME}/.cursor/skills"
  rm -rf "${HOME}/.cursor/skills/curso-aprendizaje"
  cp -R "$ROOT/skills/curso-aprendizaje" "${HOME}/.cursor/skills/curso-aprendizaje"

  mkdir -p "${HOME}/.cursor/plugins/local"
  rm -rf "${HOME}/.cursor/plugins/local/curso-aprendizaje"
  mkdir -p "${HOME}/.cursor/plugins/local/curso-aprendizaje"
  cp -R "$ROOT/plugin.json" "$ROOT/skills" "$ROOT/requirements.txt" \
    "${HOME}/.cursor/plugins/local/curso-aprendizaje/"
  cp -R "$ROOT/.cursor-plugin" "${HOME}/.cursor/plugins/local/curso-aprendizaje/"

  echo "OK Cursor skill  → ~/.cursor/skills/curso-aprendizaje"
  echo "OK Cursor plugin → ~/.cursor/plugins/local/curso-aprendizaje"
  echo "   Recarga la ventana (Developer: Reload Window) y usa /curso-aprendizaje"
}

install_claude() {
  mkdir -p "${HOME}/.claude/skills"
  rm -rf "${HOME}/.claude/skills/curso-aprendizaje"
  cp -R "$ROOT/skills/curso-aprendizaje" "${HOME}/.claude/skills/curso-aprendizaje"
  echo "OK Claude skill → ~/.claude/skills/curso-aprendizaje"
  echo
  echo "Instalación como PLUGIN (mejor, desde Claude Code):"
  echo "  /plugin marketplace add franciscosdafas133/curso-aprendizaje"
  echo "  /plugin install curso-aprendizaje@curso-aprendizaje"
  if command -v claude >/dev/null 2>&1; then
    echo
    echo "O por CLI:"
    echo "  claude plugin marketplace add franciscosdafas133/curso-aprendizaje"
    echo "  claude plugin install curso-aprendizaje@curso-aprendizaje"
  fi
}

case "$TARGET" in
  cursor) install_cursor ;;
  claude) install_claude ;;
  all) install_cursor; echo; install_claude ;;
  *)
    echo "Uso: bash install.sh [cursor|claude|all]"
    exit 1
    ;;
esac

echo
echo "Deps Python (una vez, en tu venv):"
echo "  pip install pymupdf pillow numpy scikit-learn python-pptx requests pytesseract"
echo "Listo. Abre tu carpeta de curso y corre /curso-aprendizaje"
