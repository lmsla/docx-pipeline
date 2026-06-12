# docx-pipeline

Markdown 轉企業交付 DOCX 的小型 CLI。第一版流程是：

```text
Markdown -> pandoc 套 reference.docx -> python-docx 後處理 -> output.docx
```

## 使用方式

### 方案 B：Release Binary

已打包版本位於：

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

## reference.docx

`templates/reference.docx` 是 Word 樣式模板，應保留：

- A4 頁面與邊界
- 頁首與頁尾
- `Normal`
- `Heading 1` 到 `Heading 4`
- 表格樣式
- 字型設定

目前此 repo 不內建文件內容。請把企業模板另存為 `templates/reference.docx`。
