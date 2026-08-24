# AI Agent Skill 安裝與驗收

本文件定義 `docx-pipeline` 的 AI agent Skill 安裝範圍。Skill 只負責產出符合規則的 Markdown；CLI 驗證與 DOCX 轉換不屬於 Skill 的自動工作流程。

## 共用內容

三個平台共用以下檔案：

```text
skills/docx-authoring/SKILL.md
templates/ai-agent-markdown-rules.md
templates/engineering-note-template.md
templates/enterprise-sop-template.md
```

Skill 必須讀取 Plugin 隨附的模板與規則，不應依賴使用者工作目錄中可能同名的未管理文件。

## 平台封裝

### Claude Code

使用 `.claude-plugin/plugin.json` 作為 Plugin manifest，Skill 位於：

```text
skills/docx-authoring/SKILL.md
```

Claude Code 的 Plugin root 變數只在 Claude Code 使用；共用 Skill 不應把它當成其他平台的必要環境變數。

#### 正式持久安裝

本 repo 同時提供 `.claude-plugin/marketplace.json`，因此不應把 `claude --plugin-dir .` 當成日常安裝方式。`--plugin-dir` 僅供 Plugin 開發與單次測試，關閉工作階段後不保留安裝狀態。

第一次使用時，在 Claude Code 的互動介面執行：

```text
/plugin marketplace add lmsla/docx-pipeline
/plugin install docx-pipeline@docx-pipeline-marketplace
```

安裝 Plugin 時選擇 `User scope`，即可跨專案、跨重啟持續使用。也可以用 CLI 完成相同的一次性設定：

```bash
claude plugin marketplace add lmsla/docx-pipeline --scope user
claude plugin install docx-pipeline@docx-pipeline-marketplace --scope user
```

安裝完成後，Skill 會以 `/docx-pipeline:docx-authoring` 提供，不需要再指定 repo 目錄。更新 repo 後執行：

本 Marketplace 使用 `source: "."` 將 repo root 作為 Plugin；需使用支援此來源格式的 Claude Code 版本。Claude Code `v2.1.241` 已符合目前需求。

`lmsla/docx-pipeline` 必須維持 public，marketplace 才能以 `source: github` 解析。
若改回 private，或改用 `source: directory` 指向本機路徑，安裝會綁死在單一機器的絕對路徑，
在 work 模式或其他機器上就會失效。可用以下指令確認實際登記的來源型態：

```bash
python3 -c "import json;print(json.load(open('$HOME/.claude/plugins/known_marketplaces.json'))['docx-pipeline-marketplace']['source'])"
```

```text
/plugin marketplace update docx-pipeline-marketplace
/reload-plugins
```

若要移除：

```text
/plugin uninstall docx-pipeline@docx-pipeline-marketplace
/plugin marketplace remove docx-pipeline-marketplace
```

這是 private GitHub repository；每台電腦仍須具備該 repo 的 GitHub 權限。SSH 安裝需要 SSH key 已載入 `ssh-agent`，HTTPS 安裝則需要已設定 Git credential helper。

#### 專案共用安裝

若要讓同一個 repository 的協作者在信任工作區後自動取得 Marketplace，可在該 repository 的 `.claude/settings.json` 宣告 `extraKnownMarketplaces` 與 `enabledPlugins`。這與個人 `User scope` 安裝不同，應依團隊治理需求選擇，不要兩種方式混用造成重複載入。

### Antigravity

使用 repo 根目錄的 `plugin.json` 作為 Antigravity Plugin manifest，Skill 位於：

```text
skills/docx-authoring/SKILL.md
```

也可以將 Skill 放在目標工作區的 `.agents/skills/docx-authoring/` 進行 workspace scope 測試，但必須同時讓 Skill 能讀取 repo root 的 `templates/` 資源。

### Codex

使用 `.codex-plugin/plugin.json` 作為 Codex Plugin manifest，Skill 位於：

```text
skills/docx-authoring/SKILL.md
```

Codex 的 marketplace 或工作區安裝設定由使用環境管理，不應寫入 Skill 內容，也不應因此複製模板。

## Skill 工作範圍

Skill 可以：

- 判斷 Engineering Note 或 Enterprise SOP。
- 讀取規則與對應模板。
- 整理技術討論、證據、指令、圖片與待辦事項。
- 產出 Markdown。

Skill 不可以在本工作流中：

- 執行 `docx-pipeline validate`。
- 執行 `docx-pipeline build` 或 Pandoc。
- 產出或修改 DOCX。
- 宣稱文件已通過 validator 或 Word 視覺驗收。

## 人工驗收

每個平台至少確認：

1. Plugin 或 Skill 能被發現。
2. Skill 能被正確啟用。
3. Agent 能選擇正確的文件類型。
4. Agent 會讀取隨附規則與模板。
5. 產出的 Markdown 包含正確 frontmatter、標題層級、code block 與清單格式，且沒有保留整份文件的外層 Markdown fence。
6. Agent 不會自行執行 CLI 或產出 DOCX。

Claude Code 另須驗收：

7. 可從 private Marketplace 安裝 Plugin。
8. 安裝選擇 `User scope` 後，重新啟動 Claude Code 仍能直接使用 Skill。
9. Marketplace 更新後，Plugin 版本與模板資源同步更新。

`docx-pipeline validate` 與 DOCX 轉換應由使用者或 CI 另行執行，並以其結果作為下游品質閘門。
