#!/usr/bin/env bash
set -euo pipefail

# 打包 docx-authoring 成可上傳至 claude.ai / Claude Desktop 帳號層級 Skills 的 zip。
#
# 帳號層級 Skills 與 Claude Code plugin 的資料夾結構不同：plugin 的 templates/
# 跟 skills/ 是平行目錄，透過 ${CLAUDE_PLUGIN_ROOT} 定位；帳號層級 Skill 只有
# 一個資料夾，所有隨附資源必須跟 SKILL.md 放在同一層之下，因此這裡把
# templates/*.md 複製進 skill 資料夾內再打包，而不是直接照 repo 現有佈局壓縮。
#
# 不含 templates/reference.docx——Skill 只產出 Markdown，不需要它，
# 該檔案也是使用者自備資產，不隨任何形式的封裝散布。

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="docx-authoring"
DIST="$ROOT/dist"
STAGE="$DIST/$SKILL_NAME"

rm -rf "$STAGE"
mkdir -p "$STAGE/templates"

cp "$ROOT/skills/docx-authoring/SKILL.md" "$STAGE/SKILL.md"
cp "$ROOT/templates/ai-agent-markdown-rules.md" "$STAGE/templates/"
cp "$ROOT/templates/engineering-note-template.md" "$STAGE/templates/"
cp "$ROOT/templates/enterprise-sop-template.md" "$STAGE/templates/"

ZIP_PATH="$DIST/$SKILL_NAME.zip"
rm -f "$ZIP_PATH"
(cd "$DIST" && zip -r -q "$SKILL_NAME.zip" "$SKILL_NAME")

echo "Wrote $ZIP_PATH"
echo "上傳方式：claude.ai 或 Claude Desktop -> Settings -> Features -> Skills -> Upload"
