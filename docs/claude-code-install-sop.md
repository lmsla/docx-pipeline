---
title: docx-authoring Skill 安裝作業手冊
project: docx-pipeline
document_type: SOP
author: Russell
version: 2.0
date: 2026-09-10
owner: docx-pipeline 維護者
audience: 開發人員 / 維運人員
distribution: internal
numbering: engineering
---

# 修訂記錄 <!-- no-number -->

| 修訂日期 | 版號 | 修訂內容 | 修訂者 |
|---|---|---|---|
| 2026-08-25 | 1.0 | 初版 | Russell |
| 2026-08-25 | 1.3 | 補充圖形化介面安裝方式 | Russell |
| 2026-09-10 | 2.0 | 精簡為實際安裝步驟；補上 Chat / Cowork 的 Marketplace 安裝方式（原文件誤述該環境只能走 zip 上傳） | Russell |

# 文件說明

在 Claude Code 或 Chat / Cowork 安裝 `docx-authoring` Skill。兩個環境共用同一個
Marketplace 來源 `lmsla/docx-pipeline`，不需要 zip。

# 前提條件

- 已安裝 Claude Code，或有 claude.ai / Claude Desktop 付費帳號
- 網路可連線 GitHub（本 repo 為公開 repository，不需要帳號或憑證）

# 操作步驟

## Claude Code（終端機）

```bash
claude plugin marketplace add lmsla/docx-pipeline
claude plugin install docx-pipeline@docx-pipeline-marketplace
```

安裝後重新啟動 Claude Code，並開啟**全新對話**。

## Chat / Cowork

1. 左側 **Customize** → **Plugins**
2. 右上角 **+** → **Add marketplace**
3. URL 輸入 `lmsla/docx-pipeline` → **Sync**
4. 在清單中找到 **docx-pipeline** → **Install**

# 驗證方式

在全新對話中輸入：

```text
幫我把剛才的討論整理成筆記
```

Skill 應啟動並詢問撰寫者姓名與文件類型。若只是單純討論技術問題而未提出整理要求，
Skill 不應啟動。

# 常見問題

| 現象 | 原因 | 處理 |
|---|---|---|
| `zsh: no such file or directory: /plugin` | 在一般 shell 下打了斜線指令 | 改用上方 `claude plugin ...` 指令，或先進入 `claude` 再打 `/plugin ...` |
| 安裝後行為仍是舊版 | 恢復了舊分頁，而非全新對話 | 開啟全新對話重試 |
| `Marketplace sync failed` | Marketplace 來源不符 claude.ai 規範 | 回報維護者 |

# 風險與限制

| 項目 | 說明 |
|---|---|
| 更新非自動 | `claude plugin marketplace update` 只刷新目錄，需再執行 `claude plugin update`；且僅在 `plugin.json` 版號變動時才會實際更新 |
| 組織可能鎖定安裝來源 | 管理員可透過 `strictKnownMarketplaces` 限制可安裝的 Marketplace |
| 組織統一推送需 private repo | Organization settings → Plugins 的統一分發要求 Marketplace repo 為 private 或 internal，本 repo 目前為 public，該路徑不適用 |
| 識別類資訊無機器層防線 | Skill 依賴 AI 於產出當下詢問使用者，合規責任在產出當下 |
