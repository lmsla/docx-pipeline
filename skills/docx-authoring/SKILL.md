---
name: docx-authoring
description: Create or revise Engineering Note and Enterprise SOP Markdown using the bundled docx-pipeline templates and rules. Use ONLY when the user explicitly requests that a document be produced or revised — for example "整理成筆記", "寫成 SOP", "幫我記錄", "turn this into a note", "write this up as an SOP". Do NOT use merely because a technical discussion, investigation, or troubleshooting is taking place in the conversation; wait for an explicit request to produce or revise a document.
---

# docx-pipeline 文件編寫

本 Skill 是「AI 整理筆記或 SOP 時的文件產出規範」。它只負責產出符合規範的 Markdown，
不執行 CLI、不執行 Pandoc、不產出 DOCX，也不宣稱文件已通過機器驗證。
DOCX 轉換由使用者的平台或 CI 在此工作流程之外處理。

因此**合規的責任在產出當下**：交付的 Markdown 本身就必須已經去識別化，
不能倚賴下游有沒有人跑驗證。

## 工作流程

1. 判斷文件用途，只選一種文件類型：
   - 技術筆記、調查、決策、工作進度：Engineering Note
   - 部署、操作、驗證、客戶或主管交付：Enterprise SOP
2. 讀取 Plugin 隨附的 `templates/ai-agent-markdown-rules.md`。
3. 再讀取選定的模板：
   - `templates/engineering-note-template.md`
   - `templates/enterprise-sop-template.md`
   Claude Code 可透過 `${CLAUDE_PLUGIN_ROOT}` 定位 Plugin root；Antigravity 與 Codex 應從已安裝 Plugin 的 root 定位同一個 `templates/` 目錄。若找不到隨附模板，停止整理並回報，不要自行重建規則。
4. 確認 `author`（撰寫者姓名），這是文件的追溯依據，必須在動筆前取得。依序判斷：
   - 使用者在本次對話中已表明姓名或署名意圖，直接採用。
   - 正在修訂既有文件且其 frontmatter 已有 `author`，沿用原值，不要擅自改寫。
   - 以上皆無：**停下來詢問使用者**，例如「這份文件的撰寫者姓名要填什麼？」取得答覆後再繼續。

   不得自行推測或代填，包含從 git config、email、系統帳號、專案名稱推導，也不得填入
   `撰寫者姓名`、`TBD`、`Unknown` 之類的佔位字串。使用者若不想每次都被問，可建議其在個人
   `CLAUDE.md` 記錄慣用署名（例如「我的文件署名是 Russell」），之後即可直接沿用。

5. 依模板整理內容，完整保留使用者提供的技術細節、指令、輸出、圖片與證據；不得把推測寫成已驗證結果。
6. 文件類型不明確時，先詢問使用者，不要自行混用兩種模板。
7. 交付前執行敏感資訊自檢，涵蓋正文、表格、圖說與 code block。分兩級處理：

   **憑證類——一律不得寫入，直接以 placeholder 取代，不需要詢問：**
   密碼、API key、token、session cookie、憑證私鑰、連線字串或指令中的明文帳密
   （例如 `curl -u <帳號>:<密碼>` 這種把密碼直接寫進指令的形式）。取代後在回報中列出取代了哪些項目，讓使用者知道
   原始值需要另循安全管道傳遞。

   **識別類——標示並詢問使用者，不得自行刪改：**
   客戶或機構名稱、專案代號、真實主機名與網域、內網 IP、人員姓名與 email、
   內部系統 URL、工單編號。這類資訊在內部文件中往往是必要的技術脈絡，
   是否去識別化取決於文件去向，必須由使用者決定：

   - 內部技術筆記：通常原樣保留。
   - 交付客戶、對外簡報、公開 repository：先詢問是否改用代稱。

   frontmatter 若已有 `distribution`（`internal` / `customer` / `public`），
   直接依該值判斷，不需重複詢問；沒有時才問使用者，並把答覆寫回 `distribution`。

   判斷某個字串是不是敏感資訊時（例如分不清 `es-prod-01.corp.example` 是真實主機
   還是範例），不要自行猜測，直接問使用者。

   詢問時要具體列出偵測到的項目與所在章節，例如「內文出現客戶名稱『OO 醫院』與
   主機 `es-prod-01.corp.local`，這份文件會對外嗎？需要改成代稱嗎？」

   不確定屬於哪一級時，一律標示並詢問，不要自行判定為安全。

8. 只寫入或回傳 Markdown 檔案，不觸發 `docx-pipeline`、Pandoc、DOCX build 或其他轉檔程序。驗證與 DOCX 轉換由使用者或 CI 在 Skill 工作流程之外執行。

## 寫作約束

- Frontmatter 必須保留，並依文件類型填寫必要欄位。
- `author` 是撰寫者本人姓名（例如 `Russell`）；`owner` 是負責單位或維護者。兩者語意不同，不可互相代填。
- 正文從 H1 開始，標題不可跳級；不要手動製作目錄或用 `---` 當視覺分隔線。
- 指令、設定、HTTP request、JSON、YAML 與原始輸出使用帶語言標籤的 fenced code block。
- 寫入 `.md` 的內容必須是原始 Markdown，不得把整份文件包在外層 `markdown` fenced code block。若聊天回覆為了傳輸而使用外層 fence，外層至少使用四個反引號，並在存檔前移除。
- 表格使用標準 Markdown pipe table，表格前後保留空行。
- 圖片使用相對路徑與空 alt，例如 `![](images/example.png)`；圖說另起一行。
- 一般文字中的 placeholder 要跳脫角括號，例如 `\<ELK_IP\>`；code block 內不需要跳脫。
- 不為了符合模板而刪除原始內容；不確定的內容標記為待確認、風險或待辦事項。
- 敏感資訊自檢是「標示並詢問」，不是「自動塗改」。除憑證類以外，不得因為看起來敏感就
  刪除或改寫技術內容——那會破壞文件的可重現性。

## 交付回報

回報中要明確區分：

- 已完成的 Markdown 路徑
- 選用的文件類型與模板
- 使用的 `author` 值，以及該值的來源（使用者告知／沿用原文件）
- 是否完整保留原始技術內容
- 敏感資訊自檢結果：已取代的憑證項目，以及待使用者確認的識別類資訊
- 尚未確認的事實、需要補充的欄位或待辦事項
- 明確說明本 Skill 未執行 CLI 驗證與 DOCX 轉換
