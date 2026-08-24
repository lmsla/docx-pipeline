# docx-pipeline

Markdown 轉企業交付 DOCX 的小型 CLI。第一版流程是：

```text
Markdown -> pandoc 套 reference.docx -> python-docx 後處理 -> output.docx
```

## 文件入口

- [整合規格](docs/spec.md)：CLI、Markdown、DOCX、模板、打包與整合契約
- [AI agent Markdown 規則](templates/ai-agent-markdown-rules.md)：筆記與 SOP 的撰寫規則
- [工程筆記模板](templates/engineering-note-template.md)：技術筆記、調查與決策紀錄
- [企業 SOP 模板](templates/enterprise-sop-template.md)：可直接複製使用的文件骨架
- [Claude Code Skill](skills/docx-authoring/SKILL.md)：引導 AI 選擇模板與整理文件
- [三平台 Skill 安裝與驗收](docs/skill-installation.md)：Claude Code、Antigravity、Codex 的封裝與範圍

## 使用方式

### AI agent Skill（只產出 Markdown）

本 repo 同時提供三個 AI agent 平台的 Skill manifest：

```text
.claude-plugin/plugin.json       # Claude Code
plugin.json                      # Antigravity
.codex-plugin/plugin.json        # Codex
.claude-plugin/marketplace.json  # Claude Code private Marketplace
```

三個平台共用 `skills/docx-authoring/SKILL.md`、`templates/` 與相同的 Markdown 規則。Skill 只負責整理與產出 Markdown，不會自行執行 `docx-pipeline`、Pandoc 或 DOCX 轉換。詳細安裝與人工驗收請參考 [Skill 安裝與驗收](docs/skill-installation.md)。

### Claude Code 持久安裝

`claude --plugin-dir .` 只適合維護者做單次本地測試，不是日常安裝方式。正式使用時，在 Claude Code 中一次設定 private Marketplace 與 `User scope` Plugin：

```text
/plugin marketplace add lmsla/docx-pipeline
/plugin install docx-pipeline@docx-pipeline-marketplace
```

安裝後重啟 Claude Code 不需要再次指定目錄。更新時執行：

```text
/plugin marketplace update docx-pipeline-marketplace
/reload-plugins
```

本 repo 為公開 repository，因此任何機器都能直接安裝，不需要 GitHub 憑證、SSH key 或 `ssh-agent`。
安裝時請選擇 `User scope`，即可跨專案、跨重啟、跨 chat 與 work 模式持續使用。

> 不要使用 `claude --plugin-dir .`，也不要以本機目錄註冊 marketplace。
> 目錄來源會把安裝綁死在單一絕對路徑，換資料夾或換執行環境就會失效。

### 方案 B：Release Binary

本 repo 不散布已打包的 binary。先自行打包（見下方「重新打包」），產物會位於：

```text
release/docx-pipeline/docx-pipeline
```

這個 release 目錄內已包含：

- `docx-pipeline` 可執行檔
- bundled `pandoc`
- bundled `reference.docx`
- Python runtime 與 `python-docx` 相關依賴

使用時可直接執行：

```bash
release/docx-pipeline/docx-pipeline build input.md -o output.docx
```

也可以設定 alias：

```bash
alias docx-pipeline="$HOME/tools/docx-pipeline/docx-pipeline"
```

之後即可使用：

```bash
docx-pipeline build /path/to/input.md -o /path/to/output.docx
```

若未指定 `--reference-doc`，會自動使用 release 內建的 `reference.docx`。

檢查 release 依賴：

```bash
docx-pipeline doctor
```

### Markdown 驗證

在轉檔前可先檢查 frontmatter、標題層級、code block、表格、圖片路徑與文件類型：

```bash
docx-pipeline validate input.md
docx-pipeline validate input.md --type enterprise-sop
```

驗證器只能檢查可由程式判斷的結構，不能判斷技術內容是否正確或事實是否已完成驗證。

GitHub Actions workflow 位於 `.github/workflows/markdown-quality.yml`，會執行 unit tests、合法案例與錯誤案例驗證。

### 開發模式

開發或調整程式碼時，可使用 repo 內的 wrapper：

```bash
bin/docx-pipeline build examples/manual.md -o outputs/manual.docx
```

開發模式仍會優先使用 repo 內的 `templates/reference.docx`，並從 PATH 尋找 Pandoc。

### 重新打包

macOS arm64 打包：

```bash
packaging/build-macos.sh
```

目前採用 PyInstaller `onedir` 形式，原因是它比 `onefile` 更穩定，且能避免 macOS sandbox / semaphore 啟動問題。交付時需保留整個 `release/docx-pipeline/` 資料夾，不要只複製單一 executable。

## 章節編號

Markdown 源文件可用阿拉伯數字手寫編號（`# 1. 文件說明`、`## 1.1 文件目的`），也可不寫。
轉換時 pipeline 會**剝除手寫編號並依實際結構重新生成**——源文件跳號或重複會自動修正：

```bash
docx-pipeline build input.md -o output.docx --numbering deliverable-zh   # 第一章　/ 1.1　/ 1.1.1　
docx-pipeline build input.md -o output.docx --numbering engineering     # 1. / 1.1 / 1.1.1
```

也可在 frontmatter 指定預設（CLI 參數優先）：

```yaml
numbering: deliverable-zh
```

兩者皆未指定時不編號，舊文件行為不變。例外標記：

```md
# 修訂記錄 <!-- no-number -->     ← 此標題不編號
# 參考資料 <!-- appendix -->      ← 進入附錄模式：附錄 A、附錄 B…（子層 A.1）
```

## 建議 Markdown 寫法

使用標準標題層級（不帶編號），讓 Pandoc 對應 Word 樣式：

```md
# 文件說明

## 文件目的

正文內容。

## 適用對象

- 開發人員
- 測試人員
- 維運人員
```

圖片請使用空 alt，圖說另起一行，避免 Pandoc implicit figure 影響 Word 目錄：

```md
![](images/login.png)

▲ 圖：Kibana 首頁登入畫面
```

表格使用標準 Markdown 表格：

```md
| 項目 | 說明 |
|---|---|
| 瀏覽器 | Chrome / Edge |
| 權限 | 需具備 Kibana 存取權限 |
```

一般段落、清單、表格中的角括號 placeholder 請跳脫：

```md
- Fleet Server host：https://\<ELK_IP\>:8220
```

在 fenced code block 內可直接保留：

```bash
curl -k https://<ELK_IP>:9200
```

## 敏感詞清單（客戶名稱偵測）

`validate` 只有在文件標示 `distribution: customer` 或 `public` 時才檢查客戶名稱，
且需要組織自備清單——「這是不是客戶名」沒有通用樣式可判斷。

### 查找順序

所有找到的檔案會**合併**生效，不是取第一個命中，因此公司共用清單與專案專屬補充可以並存：

| 優先序 | 來源 | 用途 |
|---|---|---|
| 1 | `--denylist PATH` | 單次覆寫，通常用於 CI |
| 2 | `DOCX_PIPELINE_DENYLIST` | 可用 `:` 分隔多個路徑 |
| 3 | `~/.config/docx-pipeline/denylist` | **使用者層共用清單，跨機器位置固定** |
| 4 | 自文件目錄向上的 `.docx-pipeline-denylist` | 專案專屬補充 |

`~/.config` 可用 `XDG_CONFIG_HOME` 覆寫。確認實際生效的來源：

```bash
docx-pipeline doctor
```

### 跨環境共用的做法

第 3 順位是關鍵：路徑與專案結構無關，在每個人的機器上都相同，即使大家的工作目錄、
作業系統或專案佈局都不一樣。共用只要把清單同步到那個固定位置即可。

清單放在公司內部的 private repository，每人執行一次：

```bash
git clone git@github.com:your-org/doc-denylist.git ~/.config/docx-pipeline/denylist-repo
ln -sf ~/.config/docx-pipeline/denylist-repo/denylist ~/.config/docx-pipeline/denylist
```

之後更新只需要 `git -C ~/.config/docx-pipeline/denylist-repo pull`。

若同事無法存取該 repository，可改指向共享磁碟或網路掛載：

```bash
export DOCX_PIPELINE_DENYLIST="/Volumes/shared/doc-denylist"
```

CI 環境建議明確指定，不要依賴 runner 的家目錄：

```bash
docx-pipeline validate doc.md --denylist "$CI_DENYLIST_PATH"
```

### 清單本身是敏感資料

實際清單等同一份客戶名單，**絕不可放進公開 repository**。`.docx-pipeline-denylist`
已列入 `.gitignore`，CI 也會擋下誤 commit。格式與註解方式見
[`templates/denylist.example`](templates/denylist.example)，該範本不含任何實際條目。

## reference.docx

`templates/reference.docx` 是 Word 樣式模板，應保留：

- A4 頁面與邊界
- 頁首與頁尾
- `Normal`
- `Heading 1` 到 `Heading 4`
- 表格樣式
- 字型設定

本 repo **不散布** `templates/reference.docx`，該路徑已列入 `.gitignore`。
請自行把企業 Word 模板另存為 `templates/reference.docx`，或每次以 `--reference-doc PATH` 指定。

確認目前是否備妥：

```bash
docx-pipeline doctor
```

## AI agent Plugin 封裝

repo 根目錄包含 Claude Code、Antigravity 與 Codex 的 Plugin manifest，以及共用的 `skills/docx-authoring/SKILL.md`。Plugin 負責引導 AI 使用規則與模板；`docx-pipeline` CLI 負責下游驗證與 DOCX 轉換。兩者版本應一起管理，但 CLI 不由 Skill 自動觸發，也不要在 Skill 中複製模板內容。
