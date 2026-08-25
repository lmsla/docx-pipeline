---
title: docx-authoring Skill 於 Claude Code 安裝作業手冊
project: docx-pipeline
document_type: SOP
author: Russell
version: 1.2
date: 2026-08-25
owner: docx-pipeline 維護者
audience: 開發人員 / 維運人員
distribution: internal
numbering: engineering
---

# 修訂記錄 <!-- no-number -->

| 修訂日期 | 版號 | 修訂內容 | 修訂者 |
|---|---|---|---|
| 2026-08-25 | 1.0 | 初版 | Russell |
| 2026-08-25 | 1.1 | 補充 Team/Enterprise 管理員限制與驗證步驟 | Russell |
| 2026-08-25 | 1.2 | 補充斜線指令與 shell 指令的差異，修正實際安裝時發現的 `zsh: no such file or directory: /plugin` 錯誤 | Russell |

# 文件說明

## 文件目的

本文件用於說明如何在 Claude Code（終端機或桌面版）安裝並驗證
`docx-authoring` Skill，讓同事在自己的機器上完成安裝、確認安裝生效，
並在遇到常見問題時能自行排除。

## 適用範圍

本文件適用於：

- 個人在自己機器上以 `User scope` 安裝 Skill
- 安裝後的自我驗證
- 常見安裝失敗的排除

本文件不包含：

- 三平台（Claude Code / Antigravity / Codex）的封裝規格，詳見
  [docs/skill-installation.md](skill-installation.md)
- claude.ai / Claude Desktop 一般聊天（work / cowork 模式）的帳號層級
  Skill 安裝，該通路走 zip 上傳，非本文件涵蓋範圍，詳見
  [README.md 的「claude.ai / Claude Desktop 一般聊天」章節](../README.md)
- `docx-pipeline` CLI 本身的安裝與使用（Skill 只產出 Markdown，不觸發 CLI）

## 前提條件

執行本文件前，需先確認：

- [ ] 已安裝 Claude Code（終端機或桌面版皆可）
- [ ] 個人帳號，或已確認組織未鎖定可安裝的 Marketplace 來源（見風險與限制）
- [ ] 網路可連線至 GitHub（本 repo 為公開 repository，不需要 GitHub 帳號或憑證）

## 名詞定義

| 名詞 | 說明 |
|---|---|
| Marketplace | Claude Code 用來發現與安裝 Plugin 的目錄來源 |
| Plugin | 本 repo 打包後在 Claude Code 內可安裝的單位，內含 `docx-authoring` Skill |
| Skill | 實際引導 AI 產出 Markdown 的規則檔案（`SKILL.md`） |
| User scope | 安裝範圍為目前使用者帳號，跨專案、跨重啟皆可用 |

# 整體流程

本文件流程分為以下階段：

1. 安裝 Marketplace 與 Plugin
2. 開啟全新對話並驗證版本
3. 實際觸發 Skill 確認行為
4. 常見問題排錯

## 流程架構

```text
Claude Code
    ↓
/plugin marketplace add lmsla/docx-pipeline
    ↓
/plugin install docx-pipeline@docx-pipeline-marketplace（User scope）
    ↓
重新啟動 Claude Code
    ↓
開啟全新對話（不可恢復舊分頁）
    ↓
驗證版本與觸發行為
```

## 角色與責任

| 角色 | 責任 | 備註 |
|---|---|---|
| 安裝者（同事本人） | 執行安裝指令、完成驗證步驟 | 每人各自在自己機器上安裝 |
| 組織管理員 | 視需要以 `strictKnownMarketplaces` 限制可安裝的 Marketplace 來源 | 非必要角色，僅組織已鎖定安裝來源時才涉及 |

# 準備事項

## 檔案與工具清單

| 類別 | 項目 | 用途 | 是否必要 |
|---|---|---|---|
| 工具 | Claude Code | 執行安裝與 Skill 的環境 | 是 |
| 資源 | `lmsla/docx-pipeline`（GitHub 公開 repository） | Marketplace 來源 | 是 |

## 環境資訊

- Marketplace 名稱：`docx-pipeline-marketplace`
- Plugin 識別碼：`docx-pipeline@docx-pipeline-marketplace`
- Skill 觸發識別碼：`docx-pipeline:docx-authoring`
- 安裝範圍：`User scope`

## 執行前檢查表

- [ ] 確認可以開啟 Claude Code 並輸入指令
- [ ] 若在公司管理的 Claude Code 環境下，先確認未被組織鎖定安裝來源（見風險與限制）

# 操作步驟

## 步驟一：安裝 Marketplace 與 Plugin

### 操作目的

讓 Claude Code 知道去哪裡找這個 Skill，並把它裝到個人帳號範圍。

### 操作方式

`/plugin ...` 是 `claude` 互動介面裡的斜線指令，**不是一般 shell 指令**——直接在
終端機提示字元（例如 `~/workspace/skill-test>`）打 `/plugin ...` 會被 shell
當成絕對路徑執行，回報 `no such file or directory`。兩種正確做法擇一：

**方式一：先進入 `claude`，在裡面打斜線指令**

```bash
claude
```

進入互動介面後執行：

```text
/plugin marketplace add lmsla/docx-pipeline
/plugin install docx-pipeline@docx-pipeline-marketplace
```

**方式二：在終端機直接下 CLI 指令，不需要先進互動介面**

```bash
claude plugin marketplace add lmsla/docx-pipeline --scope user
claude plugin install docx-pipeline@docx-pipeline-marketplace --scope user
```

兩者效果相同，方式二的開頭是 `claude` 執行檔本身、沒有斜線。

安裝 Plugin 時選擇 `User scope`（方式二已在指令中以 `--scope user` 指定）。

### 預期結果

```text
✔ Successfully added marketplace: docx-pipeline-marketplace
✔ Successfully installed plugin: docx-pipeline@docx-pipeline-marketplace (scope: user)
```

### 判斷標準

| 結果 | 判斷 | 後續動作 |
|---|---|---|
| 兩則訊息皆顯示成功 | 可繼續 | 進入步驟二 |
| 找不到 marketplace 或 clone 失敗 | 不可繼續 | 依常見問題「問題一」排除 |
| `zsh: no such file or directory: /plugin` | 不可繼續 | 在裸的 shell 提示字元下直接打了斜線指令；改用上方方式一或方式二 |

### 注意事項

- 不要使用 `claude --plugin-dir .`，那只適合單次本地測試，關閉工作階段後不保留安裝狀態。
- 不需要 GitHub 帳號、SSH key 或 credential helper——`lmsla/docx-pipeline` 是公開 repository。

## 步驟二：重新啟動並開啟全新對話

### 操作目的

安裝生效需要重新啟動 Claude Code；**且必須是全新對話，不能是重開 app 後自動恢復的舊分頁**。

### 操作方式

1. 完全結束 Claude Code（不是關閉視窗，是結束整個應用程式或終止 CLI 行程）。
2. 重新開啟 Claude Code。
3. 建立一個全新的對話，不要繼續任何既有分頁。

### 預期結果

進入一個沒有先前對話紀錄的全新對話畫面。

### 注意事項

- 恢復舊分頁帶的是該分頁最初建立時注入的系統上下文，即使整個應用程式已重啟，
  也不會反映新安裝或新版本的 Skill 內容——這是實際驗收中發現並反覆確認過的行為。

## 步驟三：驗證版本與觸發行為

### 操作目的

確認 Skill 真的被發現、載入的是最新內容、而且觸發行為符合預期。

### 操作方式

在全新對話中，貼上：

```text
docx-authoring skill 的 description 有沒有提到只在使用者明確要求時才觸發？
```

### 預期結果

回覆內容應提到「僅在使用者明確要求」（`ONLY` / 明確否定句），並列出中文觸發語（如「整理成筆記」「寫成 SOP」）。

### 判斷標準

| 結果 | 判斷 | 後續動作 |
|---|---|---|
| 回覆內容含上述描述 | 安裝成功 | 完成，可正常使用 |
| 回覆找不到這個 Skill | 不可繼續 | 依常見問題「問題一」排除 |
| 回覆內容明顯是舊版描述 | 不可繼續 | 回到步驟二，確認真的是全新對話而非恢復分頁 |

# 驗證方式

## 驗證項目

| 驗證項目 | 驗證方式 | 通過標準 |
|---|---|---|
| Skill 可被發現 | 全新對話詢問 description 內容 | 有回覆且內容非空 |
| 版本正確 | 檢視回覆是否含最新版才有的用語 | 含「僅在明確要求」等新版措辭 |
| 自然語言可正常觸發 | 描述一段技術討論並明確要求「幫我整理成筆記」 | Skill 啟動並詢問撰寫者姓名 |
| 不會誤觸發 | 只描述技術討論，不表達整理意圖 | Skill 不啟動，僅正常對話 |

## 驗證指令

無對應 CLI 指令；本流程的驗證方式為在 Claude Code 對話中觀察回覆內容，
詳見「操作步驟」步驟三。

## 驗證結果記錄

- 驗證時間：安裝當下
- 驗證人員：安裝者本人
- 驗證結果：依上表四項驗證項目逐一確認
- 備註：若團隊有多人安裝，建議统一回報驗證結果，便於追蹤是否有環境差異

# 常見問題與排錯

## 問題一：`/plugin marketplace add` 失敗或找不到 repository

### 現象

- 執行 `/plugin marketplace add lmsla/docx-pipeline` 後回報找不到或 clone 失敗

### 可能原因

- 網路無法連線至 GitHub
- 公司網路或防火牆政策封鎖 GitHub 存取
- 組織已透過 `strictKnownMarketplaces` 限制可安裝的 Marketplace 來源

### 處理方式

1. 確認自己的網路可以正常存取 `github.com`。
2. 若在公司管理的環境下，向 IT 或 Claude Code 管理員確認是否已設定
   `strictKnownMarketplaces`，以及 `lmsla/docx-pipeline` 是否在允許清單內。
3. 若組織有透過 Organization settings > Plugins 統一推送 Marketplace，
   確認是否已經由該管道取得，不需要再自行安裝。

### 判斷是否修復

- [ ] 重新執行 `/plugin marketplace add lmsla/docx-pipeline` 成功

## 問題二：安裝後找不到 Skill，或行為明顯是舊版

### 現象

- 詢問 description 內容時，回覆找不到 `docx-authoring`
- 或回覆內容是舊版描述（沒有「僅在明確要求時才觸發」的措辭）

### 可能原因

- 未真正重新啟動 Claude Code
- 重啟後恢復了舊分頁，而非開啟全新對話
- 安裝步驟中斷或未完整執行

### 處理方式

1. 確認已完全結束並重新開啟 Claude Code（不是關閉視窗）。
2. 確認目前對話是全新建立的，不是自動恢復的舊分頁。
3. 若仍失敗，重新執行步驟一的兩行安裝指令，觀察是否有錯誤訊息。

### 判斷是否修復

- [ ] 全新對話中詢問 description 內容，回覆為最新版措辭

## 問題三：Skill 觸發後行為與預期不符

### 現象

- Skill 有啟動，但沒有詢問撰寫者姓名，或自行判定文件類型未詢問

### 可能原因

- 安裝的版本落後於最新版（未執行過 `plugin update`）
- 使用者的請求中已包含類型關鍵字（例如提到「SOP」），依規則本就不需詢問

### 處理方式

1. 執行 `/plugin update docx-pipeline@docx-pipeline-marketplace` 確認是否已是最新版。
2. 若請求中已明講文件類型，未詢問屬於正常行為，非異常。
3. 若確認是最新版仍有異常行為，回報給維護者，附上完整對話截圖。

### 判斷是否修復

- [ ] 確認為已知規則內的正常行為，或已回報維護者

# 收尾檢查

交付前需確認：

- [ ] 「驗證方式」四項驗證項目已通過
- [ ] 已知悉「全新對話」與「恢復分頁」的差異
- [ ] 已知悉本文件不涵蓋 work / cowork 模式與 claude.ai 一般聊天

# 風險與限制

| 項目 | 說明 | 影響 | 建議處理 |
|---|---|---|---|
| 組織可能鎖定安裝來源 | Claude Code 管理員可透過 `strictKnownMarketplaces` 限制可安裝的 Marketplace，預設情況下個人可自行安裝，但組織可主動限制 | 受限組織下安裝步驟一會直接失敗 | 安裝前確認是否受組織政策限制，或改由組織透過 Organization settings > Plugins 統一推送 |
| 更新非自動推播 | `marketplace update` 只刷新目錄，不會自動升級已安裝的 Plugin，需再執行 `plugin update` | 使用者可能長期停留在舊版而不自知 | 定期提醒同事執行兩段式更新指令，或於團隊內部公告新版時附上指令 |
| 恢復分頁不會刷新內容 | 重開 app 後若恢復舊分頁，該分頁仍是安裝或更新前的系統上下文 | 驗證或測試時可能得到錯誤結論，誤判為安裝失敗 | 任何驗證或版本確認一律使用全新對話 |
| 客戶名稱等識別類資訊無機器層防線 | Skill 依賴 AI 於產出當下詢問使用者，不倚賴事後驗證機制 | 若使用者略過提示直接同意，識別類資訊仍可能外洩 | 內部推廣時明確告知合規責任在產出當下，Skill 只是輔助 |

# 待辦事項

- [ ] 若之後採用 Organization settings > Plugins 統一推送，需另行補充該安裝路徑的作業說明
- [ ] work / cowork 模式與 claude.ai 一般聊天的 zip 安裝流程，需另立文件

# 參考資料 <!-- appendix -->

- [README.md](../README.md)：CLI 使用方式與 zip 封裝說明
- [docs/skill-installation.md](skill-installation.md)：三平台封裝規格（維護者向）
- [docs/acceptance/skill-behaviour-0.2.0-2026-08-24.md](acceptance/skill-behaviour-0.2.0-2026-08-24.md)：行為驗收紀錄，含本文件驗證步驟的實測依據
- [Claude Code and new admin controls for business plans](https://www.anthropic.com/news/claude-code-on-team-and-enterprise)
- [Create and distribute a plugin marketplace - Claude Code Docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
