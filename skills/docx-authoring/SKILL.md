---
name: docx-authoring
description: Create or revise Engineering Note and Enterprise SOP Markdown using the bundled docx-pipeline templates and rules. Use when the user asks to record a technical discussion, document an investigation or decision, create an SOP, or standardize Markdown for later delivery.
---

# docx-pipeline 文件編寫

本 Skill 只負責產出符合規範的 Markdown。它不執行 CLI、不執行 Pandoc、不產出 DOCX，也不宣稱文件已通過機器驗證。

## 工作流程

1. 判斷文件用途，只選一種文件類型：
   - 技術筆記、調查、決策、工作進度：Engineering Note
   - 部署、操作、驗證、客戶或主管交付：Enterprise SOP
2. 讀取 Plugin 隨附的 `templates/ai-agent-markdown-rules.md`。
3. 再讀取選定的模板：
   - `templates/engineering-note-template.md`
   - `templates/enterprise-sop-template.md`
   Claude Code 可透過 `${CLAUDE_PLUGIN_ROOT}` 定位 Plugin root；Antigravity 與 Codex 應從已安裝 Plugin 的 root 定位同一個 `templates/` 目錄。若找不到隨附模板，停止整理並回報，不要自行重建規則。
4. 依模板整理內容，完整保留使用者提供的技術細節、指令、輸出、圖片與證據；不得把推測寫成已驗證結果。
5. 文件類型不明確時，先詢問使用者，不要自行混用兩種模板。
6. 只寫入或回傳 Markdown 檔案，不觸發 `docx-pipeline`、Pandoc、DOCX build 或其他轉檔程序。驗證與 DOCX 轉換由使用者或 CI 在 Skill 工作流程之外執行。

## 寫作約束

- Frontmatter 必須保留，並依文件類型填寫必要欄位。
- 正文從 H1 開始，標題不可跳級；不要手動製作目錄或用 `---` 當視覺分隔線。
- 指令、設定、HTTP request、JSON、YAML 與原始輸出使用帶語言標籤的 fenced code block。
- 寫入 `.md` 的內容必須是原始 Markdown，不得把整份文件包在外層 `markdown` fenced code block。若聊天回覆為了傳輸而使用外層 fence，外層至少使用四個反引號，並在存檔前移除。
- 表格使用標準 Markdown pipe table，表格前後保留空行。
- 圖片使用相對路徑與空 alt，例如 `![](images/example.png)`；圖說另起一行。
- 一般文字中的 placeholder 要跳脫角括號，例如 `\<ELK_IP\>`；code block 內不需要跳脫。
- 不為了符合模板而刪除原始內容；不確定的內容標記為待確認、風險或待辦事項。

## 交付回報

回報中要明確區分：

- 已完成的 Markdown 路徑
- 選用的文件類型與模板
- 是否完整保留原始技術內容
- 尚未確認的事實、需要補充的欄位或待辦事項
- 明確說明本 Skill 未執行 CLI 驗證與 DOCX 轉換
