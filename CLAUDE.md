# docx-pipeline 專案規則

查證義務見個人層級 `~/.claude/CLAUDE.md`，適用於所有專案與所有主題。
以下為本專案專屬規則。

## Skill 修改範圍

任何可能影響 DOCX 轉檔正確性的改動，必須主動指出，不能等使用者自己發現。
修改後以 `git diff --stat` 確認並明確陳述是否動到 `postprocess.py`、`cli.py`。

## repo 端的 claude.ai 硬性規則

以下兩點 Claude Code CLI 不檢查，違反時只有 Chat / Cowork 端會失敗，
且錯誤訊息不具指向性（`Marketplace sync failed`）：

- `marketplace.json` 的相對路徑 source 必須以 `./` 開頭
- repo 根目錄不得有 `bin/` 目錄，執行檔放 `scripts/`

## 文件撰寫

SOP、安裝說明類文件只寫步驟，不寫排查過程與心得。
