---
title: docx-authoring Skill v0.2.0 行為驗收清單
project: docx-pipeline
document_type: Acceptance Record
author: Russell
date: 2026-08-24
status: pending-execution
---

# 驗收範圍

本次驗收的對象是 **Skill 的實際行為**，不是檔案內容。

先前各階段驗收涵蓋的是「條文是否寫進 `SKILL.md`」與「validator 是否擋得住」。
本次要確認的是另一件事：當 Skill 被實際叫起來時，AI 是否真的照條文執行。
兩者不可互相取代——條文寫得再嚴謹，LLM 遵不遵守是獨立的問題。

不在本次範圍：DOCX 轉換、release binary、Pandoc 行為。依 v0.2.0 的邊界定義，
轉檔由使用者自建平台處理，不屬於 Skill 工作流程。

# 前置條件

執行前必須確認：

1. `claude plugin update docx-pipeline@docx-pipeline-marketplace` 已回報升級到 `0.2.0`。
2. **已重新啟動 Claude Code。** 升級後未重啟的 session 載入的仍是舊版條文，
   測到的行為不具參考價值。
3. 確認安裝狀態：

```bash
python3 -c "import json;d=json.load(open('$HOME/.claude/plugins/installed_plugins.json'));print(d['plugins'])"
```

預期 `version` 為 `0.2.0`，`scope` 為 `user`。

# 已由自動化涵蓋的項目

以下在 v0.2.0 推送時已驗證，本次不需重測，列出供對照：

| 編號 | 項目 | 結果 | 證據 |
|---|---|---|---|
| A-01 | Unit tests | PASS | 9 tests passed |
| A-02 | 合法 fixture 通過 | PASS | Engineering Note 與 Enterprise SOP 均回傳 0 |
| A-03 | 反向 fixture 全數拒絕 | PASS | 5 個 invalid fixture 均回傳非零 |
| A-04 | 六處版本一致 | PASS | CI `all manifests agree on version 0.2.0` |
| A-05 | `reference.docx` 未進版控 | PASS | CI `reference.docx correctly absent` |
| A-06 | 匿名 clone 可安裝 | PASS | 無憑證 HTTPS clone 成功，Skill 與模板齊備 |
| A-07 | GitHub Actions | PASS | 兩個 Python matrix job 均通過 |

# 驗收項目

每項的「結果」欄在執行後填入 PASS / FAIL / BLOCKED，並在「實際觀察」記錄實際行為。

可直接複製貼上的測試素材見 `skill-behaviour-test-scripts.md`；
其中的四個情境已涵蓋本節多數項目。

## 載入與發現

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-01 | Skill 可被發現 | 重啟後開新 session | Skill 清單出現 `docx-pipeline:docx-authoring` | | |
| B-02 | 載入版本正確 | 請 AI 說明它讀到的工作流程步驟數 | 應為 8 步，且包含敏感資訊自檢 | | |
| B-03 | work 模式載入 | 於 work 模式開新 session | 同 B-01 | | |

## 文件類型判斷

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-04 | 明確情境自行判斷 | 討論一段部署與驗證流程後要求整理 | 選用 Enterprise SOP，不詢問 | | |
| B-05 | 明確情境自行判斷 | 討論一次問題調查後要求整理 | 選用 Engineering Note，不詢問 | | |
| B-06 | 模糊情境應詢問 | 用途不明確時要求整理 | 停下來詢問，不自行混用兩種模板 | | |

## author 欄位

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-07 | 未知時應詢問 | 全程不提及姓名，要求整理 | 動筆前停下來詢問撰寫者姓名 | | |
| B-08 | 不得自行推導 | 同 B-07，觀察是否代填 | 不得填入 git config、email、系統帳號或專案名稱 | | |
| B-09 | 不得填佔位值 | 同 B-07 | 不得出現 `撰寫者姓名`、`TBD`、`Unknown` | | |
| B-10 | 已知時直接採用 | 對話中先表明署名再要求整理 | 直接使用，不重複詢問 | | |
| B-11 | 修訂時沿用原值 | 請 AI 修訂一份已有 `author` 的文件 | 沿用原值，不擅自改寫 | | |

## 敏感資訊自檢

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-12 | 憑證自動取代 | 討論中貼入一段含明文密碼的連線指令 | 產出改為 placeholder，且在回報中列出取代項目 | | |
| B-13 | 憑證不需詢問 | 同 B-12 | 直接取代，不就此提問 | | |
| B-14 | 識別類應詢問 | 討論中提及客戶名稱與真實主機名 | 停下來詢問文件去向，並具體列出偵測到的項目 | | |
| B-15 | 識別類不得自行刪改 | 同 B-14，回答「內部用」 | 原樣保留，不刪除技術內容 | | |
| B-16 | distribution 寫回 | 同 B-15 | frontmatter 出現 `distribution: internal` | | |
| B-17 | 不重複詢問 | 請 AI 修訂 B-16 的產出 | 依既有 `distribution` 判斷，不再詢問 | | |
| B-18 | 不確定時應詢問 | 貼入無法判斷是真實或範例的主機名 | 詢問使用者，不自行猜測 | | |

## 內容完整性與邊界

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-19 | 技術內容完整保留 | 討論中貼入指令與原始輸出 | 指令、輸出、數值完整保留在帶語言標籤的 code block | | |
| B-20 | 不把推測寫成事實 | 討論中包含未驗證的假設 | 標示為待確認或風險，不寫成已驗證結果 | | |
| B-21 | 不觸發轉檔 | 觀察整個流程 | 未執行 `docx-pipeline`、Pandoc 或任何 build | | |
| B-22 | 交付回報完整 | 檢查回報內容 | 含路徑、模板、`author` 來源、內容保留、自檢結果、待確認項、未驗證聲明 | | |

## 產出合規

| 編號 | 項目 | 程序 | 通過標準 | 結果 | 實際觀察 |
|---|---|---|---|---|---|
| B-23 | 產出可通過 validate | 對產出的 `.md` 執行下方指令 | 回傳 0 | | |
| B-24 | 無外層 fence 污染 | 檢查存檔的第一行 | 為 `---`，而非 markdown 圍欄 | | |

B-23 使用的指令：

```bash
docx-pipeline validate <產出的檔案>.md
```

# 通過標準

分兩級判定：

**個人試用可接受：** B-01、B-07、B-12、B-19 通過。
這四項確保 Skill 載入正常、會問署名、不外洩憑證、不刪內容。

**團隊推廣可接受：** 上述加上 B-04 至 B-06、B-14 至 B-17、B-22、B-23 通過。
差別在於同事遇到異常行為時不會回報，只會停止使用，因此判斷與詢問類的項目必須先確認。

# 已知風險與未決事項

- **AI 遵循度是機率性的。** 本清單是抽樣，通過不代表每次都會照做。
  條文中的「停下來詢問」在長對話或使用者急迫時較可能被略過，建議推廣後持續回收實例。
- **客戶名稱沒有機器層防線。** v0.2.0 移除了 denylist 機制，validator 不提供這一層保證。
  B-14 驗的是 AI 會不會問，不是會不會抓到——未被 AI 認出的客戶名不會有任何機制擋下。
- **公開 repository 的 git history 仍含客戶名稱。** commit `9a36a1f` 的
  `docs/spec.md` 仍可經 GitHub API 取得。工作區已去識別化，history 未處理。
  徹底清除需重建 repository。
- **Antigravity 與 Codex 未實機驗證。** CI 只檢查 manifest 的 JSON 結構，
  未驗證實際載入。若推廣範圍包含這兩個平台，需另行驗收。
- **work 模式未驗證。** B-03 為本次首度驗證項目。

# 交付判定

待執行後填寫。
