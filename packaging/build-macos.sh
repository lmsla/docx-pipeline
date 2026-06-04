#!/usr/bin/env zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
VENV="$ROOT/.build-venv"
PANDOC="${PANDOC:-$(command -v pandoc || true)}"

if [[ -z "$PANDOC" || ! -x "$PANDOC" ]]; then
  echo "error: pandoc not found. Install it first or set PANDOC=/path/to/pandoc." >&2
  exit 1
fi

"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install pyinstaller python-docx

rm -rf "$ROOT/build" "$ROOT/dist"

"$VENV/bin/python" -m PyInstaller \
  --clean \
  --noconfirm \
  --name docx-pipeline \
  --onedir \
  --paths "$ROOT/src" \
  --collect-data docx \
  --add-data "$ROOT/templates/reference.docx:templates" \
  --add-data "$ROOT/packaging/docx-parts-keep:docx/parts" \
  --add-binary "$PANDOC:bin" \
  "$ROOT/packaging/pyinstaller_entry.py"

mkdir -p "$ROOT/release"
rm -rf "$ROOT/release/docx-pipeline"
cp -R "$ROOT/dist/docx-pipeline" "$ROOT/release/docx-pipeline"
chmod +x "$ROOT/release/docx-pipeline/docx-pipeline"

echo "Wrote $ROOT/release/docx-pipeline/docx-pipeline"
