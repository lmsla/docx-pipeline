---
title: docx-pipeline 第二階段驗收紀錄
project: docx-pipeline
document_type: Acceptance Record
date: 2026-08-23
status: accepted-with-known-gaps
---

# 驗收範圍

本次驗收涵蓋：

- Markdown validator 的正向與反向案例。
- 兩份實際北榮 Markdown 文件的規則檢查。
- Claude Code Plugin manifest 與 Skill 檔案結構。
- macOS arm64 release binary 重建與基本執行。
- release binary 的 DOCX 轉換與 PNG 視覺檢查。
- GitHub Actions CI workflow 的內容落盤。

# 執行環境

- macOS arm64
- `.venv/bin/python`: Python 3.9.6
- `.build-venv/bin/python`: Python 3.14.6
- Pandoc: 3.9.0.2
- PyInstaller: 6.22.2
- 驗收日期：2026-08-23

# 驗收結果

| 編號 | 驗收項目 | 結果 | 證據或說明 |
|---|---|---|---|
| A-01 | Unit tests | PASS | 2 tests passed |
| A-02 | 合法 Engineering Note fixture | PASS | `tests/fixtures/valid/engineering-note.md` 回傳 0 |
| A-03 | 合法 Enterprise SOP fixture | PASS | `tests/fixtures/valid/enterprise-sop.md` 回傳 0 |
| A-04 | 結構錯誤 fixture | PASS | 正確拒絕未閉合 code block 與標題跳級 |
| A-05 | 缺圖 fixture | PASS | 正確回報 `MD040` |
| A-06 | 表格錯誤 fixture | PASS | 正確回報 `MD020` |
| A-07 | Plugin layout | PASS | `plugin.json` JSON、Skill 路徑與內容存在 |
| A-08 | macOS release rebuild | PASS | `packaging/build-macos.sh` 成功完成 |
| A-09 | release `doctor` | PASS | bundled Pandoc 與 `python-docx` 均可找到 |
| A-10 | release `validate` | PASS | 合法案例回傳 0，錯誤案例回傳非零 |
| A-11 | release DOCX build | PASS | 使用獨立 `/private/tmp` 工作目錄完成完整 build |
| A-12 | DOCX render QA | PASS with font note | 3 頁 PNG 產生，未見裁切或重疊；LibreOffice 環境有中文缺字方框 |
| A-13 | Claude Code 實機載入 | BLOCKED | 本機找不到 `claude` CLI，未能執行實際 Skill invocation |
| A-14 | GitHub Actions remote run | NOT RUN | workflow 已建立，但本次未 push，未觸發 GitHub runner |

# 實際文件結果

以下來源文件只讀驗收，未被本次工作修改：

## `搭建流程.standard.md`

驗證回傳非零，共回報 31 個問題，主要包括：

- 缺少 `status`、`owner`、`numbering`。
- 未完全使用 Enterprise SOP 模板的核心章節名稱。
- 多處一般文字中的 `<ELK_IP>` placeholder 未跳脫。

## `快速部署.md`

驗證回傳非零，共回報 8 個問題，主要包括：

- 缺少 `status`、`owner`、`numbering`。
- 未完全使用 Enterprise SOP 模板的核心章節名稱。

這些是來源文件契約不符合，不是 validator 或 DOCX 轉換錯誤。下一步應建立符合模板的修正版，再重新驗證。

# 驗收中發現並處理的問題

1. `validate` 原本會在啟動時匯入 `python-docx`，導致缺少 DOCX 依賴時無法執行 Markdown 檢查。已改為只在 `build` 路徑延遲載入 `postprocess`。
2. PyInstaller 清理使用者快取時受 macOS 權限影響。已將 `PYINSTALLER_CONFIG_DIR` 固定到 repo 的 `.pyinstaller-cache/`，並加入 `.gitignore`。
3. 編號建置使用來源目錄固定暫存檔，不支援同一來源的平行 build。驗收時改用獨立工作目錄與單一執行，release build 成功。
4. 初次 release build 曾出現 bundled Pandoc `SIGKILL` 與暫存檔權限錯誤；直接執行 bundled Pandoc 正常，改用獨立工作目錄、單一 build 後完整 release build 成功，未判定為 Pandoc 或 pipeline 功能錯誤。

# 未完成與風險

- 尚未在 Claude Code CLI 或 Desktop 實機載入 `/docx-pipeline:docx-authoring`；需要可用的 Claude Code 執行環境後補驗。
- GitHub Actions 尚未在遠端 runner 執行；push 後需確認兩個 Python matrix job 都通過。
- LibreOffice 渲染環境缺少 reference.docx 使用的部分中文字型；Word on macOS 的最終視覺驗收仍不可由本次 PNG 結果取代。
- 兩份實際來源文件尚未依新模板修正，因此目前不能宣稱它們已通過 `validate`。
- release binary 仍是 macOS arm64；其他 OS/架構需要各自打包與驗收。

# 交付判定

第二階段的 validator、驗收案例、CI workflow 與 release binary 實作已完成。工具鏈驗收通過；實際文件與 Claude Code 實機載入保留為明確的後續工作，不以推測冒充完成。
