---
title: docx-pipeline 整合規格
project: docx-pipeline
document_type: Spec
version: 0.1.1
date: 2026-08-23
owner: lmsla
audience: 開發者 / 維護者 / 工作流整合者
status: draft
numbering: engineering
---

# docx-pipeline 整合規格

## 0. 文件目的

本文件定義 `docx-pipeline` 目前版本的可整合行為，讓其他 CLI、AI agent、CI/CD 或文件工作流可以用固定契約呼叫本工具。

本文件以目前程式碼與 `0.1.1` 專案版本為準。標示為「限制」的內容不屬於可依賴的保證；標示為「未支援」的能力不應由整合方自行假設存在。

## 1. 產品定位

`docx-pipeline` 是將標準 Markdown 轉換為企業交付格式 DOCX 的命令列工具。

目前處理流程如下：

```text
Markdown
    ↓
讀取 frontmatter、可選的標題編號預處理
    ↓
Pandoc + reference.docx
    ↓
python-docx / OOXML 後處理
    ↓
DOCX
```

### 1.1 主要能力

- 以 `reference.docx` 作為企業 Word 樣式基礎。
- 產生封面、頁首、頁尾頁碼與目錄。
- 支援標題編號 profile：`engineering`、`deliverable-zh`。
- 對程式碼區塊、表格與圖片進行版面整理。
- 以 `validate` 子命令檢查 Markdown 的可機器判斷結構。
- 提供開發模式與 macOS release package。

### 1.2 非目標

- 不是 Markdown 編輯器或內容品質審查器。
- 不保證 AI agent 會遵守模板；Skill 只提供工作流程，validator 才是可執行的結構檢查。
- 不是任意 Word 文件的版面設計引擎。
- 不保證將任意 Markdown 方言轉成相同版面。
- 不提供 GUI、Web API、PDF 輸出或雲端轉換服務。
- 不提供跨平台的單一可執行檔。
- 不將 `src/docx_pipeline` 視為穩定的 Python library API。

## 2. CLI 契約

### 2.1 建置命令

```bash
docx-pipeline build <input.md> -o <output.docx> [options]
```

必要參數：

| 參數 | 說明 |
|---|---|
| `input.md` | UTF-8 編碼的 Markdown 輸入檔案 |
| `-o`, `--output` | 產出的 DOCX 路徑，父目錄不存在時會建立 |

可選參數：

| 參數 | 預設行為 | 說明 |
|---|---|---|
| `--reference-doc PATH` | 使用內建模板 | 指定 Pandoc reference DOCX |
| `--header TEXT` | 使用 Markdown `title` | 設定一般頁首文字 |
| `--no-header` | 不使用 | 不寫入一般頁首；優先於 `--header` |
| `--numbering PROFILE` | 不編號 | 使用 `engineering` 或 `deliverable-zh` |
| `--no-cover` | 產生封面 | 跳過 pipeline 產生的封面 |
| `--no-toc` | 產生原生目錄 | 完全不產生目錄 |
| `--static-toc` | 使用原生目錄 | 產生無頁碼的靜態目錄 |
| `--keep-intermediate` | 清理暫存檔 | 保留 Pandoc 中間 DOCX 與編號暫存 Markdown |
| `--no-table-cleanup` | 整理表格 | 跳過表格樣式整理 |
| `--no-image-cleanup` | 整理圖片 | 跳過圖片尺寸與段落整理 |
| `--no-chapter-breaks` | H1 換頁 | 跳過 H1 章節前的分頁設定 |

`--numbering` CLI 參數優先於 frontmatter 的 `numbering`。`--no-toc` 與 `--static-toc` 同時使用時，目前實作以 `--no-toc` 為準，不產生目錄。

建置成功時會將 DOCX 寫入指定路徑，並在標準輸出顯示：

```text
Wrote /path/to/output.docx
```

整合方應以退出碼與輸出檔案是否存在作為判斷依據，不應依賴這段文字進行解析。

### 2.2 依賴檢查命令

```bash
docx-pipeline doctor
```

此命令會顯示 Pandoc 與 `python-docx` 的可用狀態。現行實作即使偵測到依賴缺失仍回傳退出碼 `0`，因此整合方不能只依賴 `doctor` 的退出碼判斷是否可建置；實際建置仍應檢查 `build` 結果。

### 2.3 Markdown 驗證命令

```bash
docx-pipeline validate <input.md> [--type engineering-note|enterprise-sop]
```

驗證項目：

- UTF-8 編碼與 frontmatter 起訖位置。
- 必要 frontmatter 欄位與文件類型。
- H1 起始、標題層級不可跳級與文件類型的核心章節。
- fenced code block 必須有語言標籤且必須閉合。
- 整份文件不得保留聊天傳輸用的外層 `markdown` fenced code block；若誤存，回傳 `MD012`。
- frontmatter 欄位若仍是模板佔位值（例如 `撰寫者姓名`、`專案名稱`、`YYYY-MM-DD`、`TBD`），回傳 `MD009`。
- 文件內含寫死的憑證時回傳 `MD060`–`MD063`：私鑰（`MD060`）、AWS access key ID（`MD061`）、
  Bearer token（`MD062`）、密碼與 API key 指派或指令中的明文帳密（`MD063`）。
  此檢查**不跳過 fenced code block**，因為憑證最常出現在指令與設定範例中；
  已改為 placeholder、遮罩或環境變數的值不會觸發。
- Markdown pipe table 的表頭、分隔列與資料列欄數。
- 相對圖片路徑是否存在；HTTP、HTTPS 與 data URL 不由本命令下載或檢查。
- 一般文字中的未跳脫 placeholder 角括號。

`--type` 可在 frontmatter 使用客製 `document_type` 時指定分類，但不會免除必要 frontmatter 欄位。驗證成功回傳 `0`；任一檢查失敗回傳 `1`，並在標準錯誤輸出列出 `CODE: path:line: message`。

限制：validator 不判斷技術內容正確性、指令是否真的執行過、圖片內容是否符合說明，也不取代人工審查或 DOCX 視覺驗收。

### 2.4 依賴尋找順序

Pandoc 的尋找順序如下：

1. `DOCX_PIPELINE_PANDOC` 環境變數指定的存在路徑。
2. release package 內的 bundled Pandoc。
3. 作業系統 `PATH` 中的 `pandoc`。

開發模式需要 Python 與 `python-docx`，並通常需要系統已安裝 Pandoc。release package 已包含 Python runtime、`python-docx`、相關依賴與 bundled Pandoc。

### 2.5 輸出與暫存檔

- 若輸出檔已存在，建置會覆寫該檔案。
- Pandoc 中間檔使用輸出路徑同名的 `.pandoc.docx`。
- 啟用編號時，會在來源 Markdown 同目錄建立 `.<stem>.numbered.md`。
- 預設建置完成後會刪除上述暫存檔。
- 使用 `--keep-intermediate` 時會保留暫存檔，便於除錯。

限制：同一來源目錄、同一檔名的編號建置不適合平行執行，因為暫存 Markdown 檔名固定。需要平行轉檔時，整合方應使用不同來源副本或不同工作目錄。

## 3. Markdown 輸入契約

### 3.1 編碼與基本結構

- 檔案必須使用 UTF-8。
- frontmatter 必須從第一行開始，並以獨立的 `---` 行結束。
- 文件至少應有一個 H1，並應由 H1 開始章節結構。
- 標題層級不可跳級：H1 後使用 H2，H2 後使用 H3。
- 正文、清單、表格與圖片不可用空白對齊方式模擬版面。
- 不要使用 `---` 作為章節間的視覺分隔線；版面區隔由 DOCX 樣式處理。
- 可使用 `docx-pipeline validate` 在轉檔前檢查上述結構；未執行 validator 不代表內容已通過驗證。

### 3.2 Frontmatter

目前只保證單行 `key: value` 格式，不保證完整 YAML 語法、巢狀物件、陣列或多行值。

建議使用以下欄位：

| 欄位 | 用途 |
|---|---|
| `title` | 文件標題；作為預設頁首與目錄識別依據 |
| `project` | 封面主標題，優先於 `cover_title` 與 `title` |
| `cover_title` | 封面主標題的替代欄位 |
| `subtitle` | 封面副標題 |
| `guide` | 封面導引文字，優先於 `document_type` |
| `document_type` | 封面導引文字的替代欄位 |
| `author` | 撰寫者姓名；寫入封面「撰寫者」列與 DOCX core properties |
| `distribution` | 文件去向（`internal` / `customer` / `public`）；供 AI 判斷是否需要去識別化，工具本身不使用 |
| `file_name` | 封面「文件名稱」欄位，未提供時使用 `title` |
| `version` | 封面版本欄位 |
| `date` | 封面建立日期；未提供時使用執行當日日期 |
| `system` | 封面「適用系統」欄位 |
| `applicable_system` | `system` 的替代欄位 |
| `audience` | 封面「適用對象」欄位 |
| `applicable_audience` | `audience` 的替代欄位 |
| `numbering` | 預設標題編號 profile |

`title` 未提供時，工具會使用第一個 H1；若仍找不到，使用輸入檔案的檔名 stem。`owner`、`status` 等欄位可保留在文件 metadata，但目前不會自動寫入封面或頁首。

`author` 提供時，封面 metadata 表格會多一列「撰寫者」，並同步寫入 DOCX 的 core properties（`author` 與 `last_modified_by`），供 Word 檔案內容頁籤追溯。未提供時封面不產生該列。`validate` 將 `author` 列為共通必要欄位（缺少時回傳 `MD005`）。

範例：

```yaml
---
title: Elastic Agent 部署 SOP
project: 範例專案 POC
document_type: 使用者操作手冊
version: 1.0
author: Russell
date: 2026-08-23
system: Elasticsearch / Kibana / Fleet
audience: 維運人員
numbering: deliverable-zh
---
```

### 3.3 標題與編號

原始 Markdown 建議不手寫標題編號，交由 pipeline 依實際層級產生。若原始文件已有下列形式的編號，啟用 numbering 時會嘗試先剝除再重編：

- `1. 標題`
- `1.1 標題`
- `1、標題`

可用以下標記控制例外：

```md
# 修訂記錄 <!-- no-number -->
# 參考資料 <!-- appendix -->
```

編號 profile：

| Profile | H1 | H2 / H3 |
|---|---|---|
| `engineering` | `1. 標題` | `1.1 標題` / `1.1.1 標題` |
| `deliverable-zh` | `第一章　標題` | `1.1　標題` / `1.1.1　標題` |

目前實作的上限是 99 個章節與 26 個附錄；超出上限不屬於支援範圍。

### 3.4 程式碼區塊

指令、設定檔、HTTP request、JSON、YAML 與原始輸出必須使用 fenced code block，並保留語言標籤：

````md
```bash
curl -k https://ELK_IP:9200/_cluster/health?pretty
```
````

工具會將 Pandoc 產生的 `Source Code` 段落套用灰底、邊框與等寬字型。語言標籤是輸入規範，但目前不保證產生語言名稱標籤或語法高亮。

聊天介面若需要將完整 Markdown 包在回覆中，外層 fence 必須比內文最長 fence 更長；內文使用三個反引號時，外層至少使用四個反引號。這只是傳輸包裝，不能寫入交付的 `.md` 檔。

### 3.5 表格

表格應使用標準 pipe table，且每列欄位數一致：

```md
| 項目 | 說明 |
|---|---|
| 權限 | 需具備 Kibana 存取權限 |
```

轉換時會對一般表格套用中央對齊、外框、內框、表頭底色、表頭粗體、儲存格內距與交錯列底色。封面五列文件資訊表是特殊表格，不套用一般內容表格的交錯列樣式。

長篇敘述應使用段落或清單，不要塞入表格儲存格。

### 3.6 圖片

圖片路徑以 Markdown 檔案所在目錄為基準解析。建議使用空 alt，並將圖說獨立成下一行：

```md
![](images/login.png)

▲ 圖：Kibana 登入畫面
```

pipeline 會將圖片置中，並在超過可用內容寬度時等比例縮小。圖片檔案必須存在且由執行工具的程序可讀取。

不要將圖片與 `---`、標題、表格或 code block 緊貼，避免 Pandoc 將圖片解讀為 implicit figure，造成目錄或版面異常。

### 3.7 Placeholder

一般段落、清單與表格中的角括號 placeholder 必須跳脫：

```md
- Fleet Server host：https://\<ELK_IP\>:8220
```

fenced code block 內可直接使用角括號：

````md
```bash
curl -k -u 'elastic:<PASSWORD>' https://<ELK_IP>:9200
```
````

## 4. DOCX 輸出契約

### 4.1 預設輸出

在未指定額外選項時，輸出包含：

- `reference.docx` 提供的 Word 樣式基礎。
- pipeline 產生的封面。
- 由 Markdown `title` 產生的一般頁首。
- `- PAGE -` 格式的 Word 原生頁碼欄位。
- Word 原生目錄，目錄深度為三層。
- 每個 H1 章節從新頁開始。
- 程式碼、表格與圖片的後處理樣式。

### 4.2 封面欄位對應

封面是由 pipeline 依 metadata 建立，不是直接使用 Markdown 正文第一頁。欄位對應如下：

| 封面欄位 | Metadata 來源 |
|---|---|
| 主標題 | `project` → `cover_title` → `title` |
| 副標題 | `subtitle` |
| 導引文字 | `guide` → `document_type` |
| 文件名稱 | `file_name` → `title` |
| 版本 | `version` |
| 建立日期 | `date` → 執行當日日期 |
| 適用系統 | `system` → `applicable_system` |
| 適用對象 | `audience` → `applicable_audience` |

因此頁首預設不是寫死的企業名稱，而是來自輸入文件的 `title`。若需自訂頁首，使用 `--header`；若不需要頁首，使用 `--no-header`。

### 4.3 目錄與頁碼

預設目錄是 Word 原生 field，頁碼由 Word 在開啟或更新功能變數時計算。開啟文件時可能出現「更新功能變數」提示，這是原生目錄的正常行為，不是 DOCX 損壞。

在 Word 中應選擇更新功能變數，或選取目錄後執行「更新整個目錄」。若整合方不能接受 Word 更新提示，可使用 `--static-toc`，但該模式沒有正確頁碼。

### 4.4 樣式與版面

pipeline 會嘗試套用以下基礎設定：

- A4 紙張，四邊約一英吋邊界。
- 一般文字使用 Microsoft JhengHei，11pt。
- H1 至 H4 使用固定大小與企業藍色系樣式。
- `Source Code` 使用 Fira Mono、灰底與邊框。
- 一般內容表格使用淡藍表頭與淡色交錯列。
- 圖片依內容區寬度等比例縮小，不放大。

實際字型、頁首頁尾背景、圖框與其他企業視覺元素仍由 `reference.docx` 決定。修改 reference template 可能改變輸出結果，即使 CLI 程式碼沒有變更。

## 5. Reference DOCX 契約

### 5.1 開發模式

未指定 `--reference-doc` 時，開發模式預設使用：

```text
templates/reference.docx
```

本 repo **不散布** `templates/reference.docx`（已列入 `.gitignore`，並由 CI 檢查不得再次進入版控）。
該路徑是使用者自備的企業 Word 樣式母體。檔案不存在時 `build` 會以非零退出碼中止，
並提示改用 `--reference-doc`；`doctor` 會回報目前是否備妥。

若使用自訂企業模板，應明確傳入：

```bash
docx-pipeline build input.md \
  --reference-doc /path/to/reference.docx \
  -o output.docx
```

### 5.2 模板要求

`reference.docx` 必須是可被 Pandoc 與 `python-docx` 讀取的有效 DOCX。為維持目前輸出品質，模板至少應保留：

- A4 頁面與基本邊界設定。
- `Normal`。
- `Heading 1` 至 `Heading 4`。
- `Source Code`，以維持程式碼區塊樣式。
- 頁首、頁尾與表格的企業樣式。

模板不得依賴未隨 release 一起交付的外部字型、圖片或連結資源。模板若含企業機密，交付或公開 repo 前必須先完成去識別化與內容檢查。

### 5.3 Release 模板

macOS release package 內建一份 `reference.docx`。搬移或交付 release 時，必須保留整個 package 目錄，不可只複製 executable。

## 6. 錯誤與退出碼契約

| 情況 | 目前行為 |
|---|---|
| 成功建置 | 退出碼 `0` |
| Markdown 不存在 | stderr 顯示錯誤，退出碼 `1` |
| Reference DOCX 不存在 | stderr 顯示錯誤，退出碼 `1` |
| Pandoc 不存在或執行失敗 | stderr 顯示錯誤，退出碼 `1` |
| CLI 參數格式錯誤 | argparse 錯誤，通常退出碼 `2` |
| `--numbering` 指定未知 profile | CLI 參數錯誤，退出碼 `2` |
| frontmatter 指定未知 profile | stderr 顯示錯誤，退出碼 `1` |

整合方至少應檢查：

1. 程序退出碼是否為 `0`。
2. 指定的輸出檔是否存在且大小大於零。
3. 需要交付時，再以 Word 或其他 DOCX 驗證工具確認文件可開啟。

目前沒有自動化 OOXML schema 驗證，也沒有完整的跨版本 Word 視覺回歸測試；文件可開啟與版面正確仍需列入交付驗收。

## 7. Packaging 與部署契約

### 7.1 開發模式

開發模式使用 repo wrapper：

```bash
bin/docx-pipeline build examples/manual.md -o outputs/manual.docx
```

需要 Python `>=3.9`、`python-docx` 與 Pandoc。Python virtual environment 只影響開發模式，不是 release 使用者的必要條件。

### 7.2 Release 模式

目前 release 是 PyInstaller `onedir` package，路徑為：

```text
release/docx-pipeline/
```

該目錄包含 executable、bundled Pandoc、`reference.docx`、Python runtime 與依賴。正式交付時必須整個搬移：

```bash
release/docx-pipeline/docx-pipeline build input.md -o output.docx
```

目前正式支援的打包目標是建立該 release 的 macOS arm64 環境。Windows、Linux 或其他 CPU 架構需要各自重新打包與驗證。

### 7.3 工作流整合建議

其他工具應優先以 subprocess 呼叫已釘選版本的 CLI，而不是 import `src/docx_pipeline` 內部函式。整合方應：

- 釘選 release 版本或 Git commit。
- 為每次轉換提供唯一輸出路徑。
- 確保 Markdown、圖片與 reference DOCX 的路徑可讀取。
- 以退出碼與輸出檔存在性判斷成功。
- 將 Word 原生目錄更新列為交付流程的一部分，或明確選擇 `--static-toc`。
- 在 Pull Request 中先執行 `validate` 與 unit tests；不需要在 CI 中平行建置同一份來源 Markdown。

### 7.4 AI agent Skill 整合

repo 同時提供 Claude Code、Antigravity 與 Codex 的 Skill / Plugin manifest，結構如下：

```text
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
plugin.json
.codex-plugin/plugin.json
skills/docx-authoring/SKILL.md
templates/ai-agent-markdown-rules.md
templates/engineering-note-template.md
templates/enterprise-sop-template.md
```

Skill 只負責選擇文件類型、載入規則與整理 Markdown。它不應複製模板、不應執行 CLI、不應產出 DOCX，也不應宣稱已完成未執行的驗證。`validate` 與 `build` 屬於使用者或 CI 的下游流程，不是 AI agent Skill 的責任。

Claude Code 的 `.claude-plugin/marketplace.json` 是持久安裝入口。正式使用時，使用者將公開 GitHub repository `lmsla/docx-pipeline` 加入 Marketplace，並以 `User scope` 安裝 `docx-pipeline`；Marketplace 必須以 `source: github` 註冊，不可使用指向本機路徑的 `source: directory`，否則安裝會綁定單一絕對路徑，換執行環境即失效；`claude --plugin-dir` 僅供本地開發與單次測試，不是交付流程。Marketplace 更新後，使用者以 Marketplace update 取得新的 Plugin 與模板版本。

## 8. 版本與相容性

目前專案版本為 `0.1.1`，仍屬早期版本。整合方不應假設 `0.x` 版本具有完整的長期相容保證。

以下變更應視為可能影響整合的 breaking change：

- CLI 子命令、參數名稱或退出碼改變。
- frontmatter 欄位優先順序改變。
- 圖片、表格、程式碼區塊的輸入規則改變。
- 預設封面、目錄、頁首、頁尾或編號行為改變。
- `reference.docx` 的樣式、欄位或內嵌資源改變。
- release 從 `onedir` 改成其他部署結構。

程式版本與 `reference.docx` 應視為同一份交付版本管理。只升級程式、不同步驗證模板，不能保證輸出 DOCX 外觀不變。

## 9. 已知限制

- Word 原生目錄的頁碼需要 Word 更新功能變數。
- release 是整個 `onedir` 目錄，不是可單獨搬移的單一 executable。
- release 目前以 macOS arm64 為主要打包目標。
- 沒有完整的自動化測試與 DOCX 視覺回歸測試。
- validator 只能檢查結構與檔案存在性，不能保證技術事實、指令結果或圖片語意正確。
- 憑證偵測採高精確度樣式，刻意寧可漏報也不誤擋；客戶名稱、主機名這類語意判斷無法自動化，
  仍須由撰寫者與複核者負責，不可將 `validate` 通過視為已完成去識別化。
- Claude Code Skill 是否被載入與遵循，取決於 AI 工作流與使用者授權，不能視為強制閘門。
- `doctor` 目前不以缺少依賴作為非零退出碼。
- 編號建置使用固定名稱的同目錄暫存 Markdown，不適合相同來源的平行建置。
- 編號章節與附錄有數量上限。
- `reference.docx` 的內容與樣式會直接影響結果，換模板後需重新驗證。
- 工具不是不受信任 Markdown 的安全隔離環境；輸入檔與圖片路徑必須由整合方控管。

## 10. 最小驗收標準

每次發布或整合前，至少驗證以下項目：

- [ ] `docx-pipeline build` 可將一份 UTF-8 Markdown 轉成 DOCX。
- [ ] 封面欄位會依 frontmatter 正確帶入。
- [ ] 頁首使用文件標題，沒有殘留不相干的模板文字。
- [ ] 原生目錄可在 Word 中更新，頁碼正確。
- [ ] `--static-toc` 可產生無頁碼目錄。
- [ ] 程式碼區塊有灰底、邊框與等寬字型。
- [ ] 表格有表頭樣式、邊框與列區隔。
- [ ] 相對圖片可嵌入 DOCX 且不超出內容寬度。
- [ ] `engineering` 與 `deliverable-zh` 編號結果符合預期。
- [ ] 缺少輸入檔或 Pandoc 時，`build` 會回傳非零退出碼。
- [ ] 合法的 Engineering Note 與 Enterprise SOP 可通過 `validate`。
- [ ] 結構錯誤、缺圖、未閉合 code block、外層 Markdown 包裝與不一致表格會使 `validate` 回傳非零退出碼。
- [ ] release 目錄在目標 macOS 環境可直接執行，且 `_internal` 內容完整。

## 11. 文件分工

| 文件 | 責任 |
|---|---|
| `README.md` | 快速安裝、執行與打包說明 |
| `docs/spec.md` | CLI、輸入、輸出、部署與整合契約 |
| `templates/ai-agent-markdown-rules.md` | AI agent 撰寫 Markdown 的規則 |
| `templates/engineering-note-template.md` | 技術筆記、調查與決策紀錄模板 |
| `templates/enterprise-sop-template.md` | SOP / 交付文件的 Markdown 起始模板 |
| `templates/reference.docx` | Word 視覺樣式與企業模板 |
| `src/docx_pipeline/validator.py` | Markdown 結構與資產驗證 |
| `.claude-plugin/plugin.json` | Claude Code Plugin metadata |
| `.claude-plugin/marketplace.json` | Claude Code Marketplace catalog（公開 repo） |
| `plugin.json` | Antigravity Plugin metadata |
| `.codex-plugin/plugin.json` | Codex Plugin metadata |
| `skills/docx-authoring/SKILL.md` | 三平台共用的 Markdown 文件編寫工作流程 |
| `docs/skill-installation.md` | 三平台 Skill 安裝與人工驗收範圍 |
| `tests/fixtures/` | validator 正向與反向驗收案例 |
| `.github/workflows/markdown-quality.yml` | Pull Request 的 Markdown 品質閘門 |
| `docs/acceptance/` | 實際驗收紀錄與已知限制 |
| `examples/manual.md` | 可供轉換驗證的最小範例 |
