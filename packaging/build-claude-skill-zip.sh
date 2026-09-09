#!/usr/bin/env bash
set -euo pipefail

# 打包 docx-authoring 成可上傳至 claude.ai / Claude Desktop 帳號層級 Skills 的 zip。
#
# Skill 自帶 templates/（與 SKILL.md 同一層），四種安裝方式的相對位置一致，
# 因此這裡直接複製整個 skill 目錄，不需要為特定平台重組檔案佈局。
#
# templates/reference.docx 不在 skill 目錄下，也不隨任何形式的封裝散布——
# Skill 只產出 Markdown，不需要它，該檔案是使用者自備資產。

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="docx-authoring"
DIST="$ROOT/dist"
STAGE="$DIST/$SKILL_NAME"

rm -rf "$STAGE"
mkdir -p "$DIST"
cp -R "$ROOT/skills/$SKILL_NAME" "$STAGE"

ZIP_PATH="$DIST/$SKILL_NAME.zip"
rm -f "$ZIP_PATH"
(cd "$DIST" && zip -r -q "$SKILL_NAME.zip" "$SKILL_NAME")

echo "Wrote $ZIP_PATH"
echo "上傳方式：claude.ai 或 Claude Desktop -> Settings -> Skills -> Upload"
