# AI Agent Markdown 寫作規則

本文件是所有 Markdown 文件共用的寫作規則，不是文件模板。目標是讓 Markdown 可讀、可維護，並能穩定轉換成企業格式 DOCX。

AI agent 必須先判斷文件類型，再選擇一份模板使用；不可同時混用兩份模板的章節結構。

## 核心原則

- 內容必須完整保留，不得為了排版刪減技術細節。
- 使用標準 Markdown 語義，不要用 code block 假裝排版。
- 文件標題與 metadata 放在 YAML front matter。
- 章節從 `#` 開始，子章節依序使用 `##`、`###`、`####`。
- 不要跳級使用標題，例如 `#` 後直接接 `###`。
- 標題可用阿拉伯數字手寫編號（`# 1. 標題`、`## 1.1 標題`）或不寫；docx-pipeline 轉換時會剝除手寫編號、依實際結構重新生成（profile 由 frontmatter `numbering:` 指定），跳號會自動修正。不編號的標題加 `<!-- no-number -->`，附錄加 `<!-- appendix -->`。
- 指令、設定檔、HTTP request、JSON、YAML、原始輸出才使用 fenced code block。
- 交付的 `.md` 必須是原始 Markdown，不得把整份文件再包在外層、標示為 `markdown` 的 fenced code block；否則內文的 code block 會被錯誤截斷。
- 若聊天介面為了傳輸完整 Markdown 而需要外層包裝，外層反引號數量必須多於文件內最長的 fence，且存檔前必須移除外層包裝。內文使用三個反引號時，外層至少使用四個反引號。
- 一般說明、注意事項、判斷原則、前提條件請使用段落或清單。
- 檢查表使用 `- [ ]`，不要寫成 `[ ]`，也不要包在 code block。
- 流程步驟使用真正的 numbered list。
- 可比較資料使用表格，不要用空白對齊文字。
- 一般段落或清單中的 placeholder 若使用角括號，需跳脫成 `\<ELK_IP\>`，避免被 Markdown 轉換器視為 HTML tag。
- 不要在章節之間用 `---` 當視覺分隔，DOCX 轉換時會由標題、段落間距與頁面樣式處理區隔。

## 文件類型選擇

先判斷文件用途，只能選擇一種模板：

| 文件類型 | 使用模板 | 適用情境 |
|---|---|---|
| Engineering Note | `templates/engineering-note-template.md` | 技術筆記、調查、決策、工作進度 |
| Enterprise SOP | `templates/enterprise-sop-template.md` | SOP、部署流程、客戶或主管交付 |

選定後依序執行：

1. 複製對應模板。
2. 保留模板的 frontmatter 與章節結構。
3. 依本文件的共通規則填寫內容。
4. 執行對應文件類型的自檢。

### Engineering Note

重點是保留問題脈絡、可驗證證據、判斷理由、執行結果與待辦事項。內容不完整或仍在調查中時，可以保留不確定性與未完成項目。

### Enterprise SOP

重點是讓其他人可以依文件完成操作。內容應包含適用範圍、前提條件、操作步驟、預期結果、驗證方式、排錯方式與風險限制。

## 模板使用規則

- 模板是文件起始骨架，不是必須逐字保留的內容。
- 不適用的章節可以刪除；原始技術內容、指令與證據不可刪減。
- 不要把 Engineering Note 的輕量結構與 Enterprise SOP 的正式結構混在同一份文件中。
- 文件完成後應移除未填寫的 placeholder 與空白章節。
- 兩種文件都必須遵循本文件的 Markdown、圖片、表格與 code block 規則。

## Frontmatter 規則

所有文件應使用 YAML frontmatter。`docx-pipeline validate` 會檢查共通必要欄位；Enterprise SOP 也會檢查正式交付所需欄位。以下欄位值仍需要由 AI agent 或作者依實際內容填寫，validator 不判斷內容是否真實。

### 共通欄位

```yaml
title: 文件標題
project: 專案名稱
document_type: 文件類型
date: YYYY-MM-DD
status: draft
```

### Engineering Note 建議欄位

```yaml
document_type: Engineering Note
numbering: engineering
```

Engineering Note 的 `owner`、`audience` 與 `numbering` 可依情境省略；若要轉成正式交付文件，請改用 Enterprise SOP 模板。

### Enterprise SOP 建議欄位

```yaml
document_type: SOP
version: 1.0
owner: 撰寫人或負責單位
audience: 客戶 / 主管 / 維運人員 / 開發人員
numbering: deliverable-zh
```

Enterprise SOP 的 `version`、`owner`、`audience`、`status` 與 `numbering` 不應省略。日常 Engineering Note 不需要強制套用完整 SOP metadata。

## 清單規則

一般條列：

```md
- 項目 1
- 項目 2
- 項目 3
```

有順序的流程：

```md
1. 第一步
2. 第二步
3. 第三步
```

檢查表：

```md
- [ ] 檢查項目 1
- [ ] 檢查項目 2
- [ ] 檢查項目 3
```

## Code Block 規則

保留語言標籤：

````md
```bash
kubectl get pods
```
````

````md
```yaml
key: value
```
````

````md
```http
GET /_cat/health?v
```
````

只有原始輸出、目錄樹或架構文字圖使用 `text`：

````md
```text
service: HEALTHY
status: OK
```
````

不要這樣寫：

````md
```text
[ ] 檢查項目
判斷原則 1
判斷原則 2
```
````

應改成：

```md
- [ ] 檢查項目

判斷原則：

- 判斷原則 1
- 判斷原則 2
```

## 表格規則

表格用於比較資料、欄位定義、檢查矩陣、風險列表。

```md
| 項目 | 說明 | 備註 |
|---|---|---|
| 項目 1 | 說明 | 備註 |
| 項目 2 | 說明 | 備註 |
```

避免把長篇段落塞進表格。如果內容是敘述，請改用段落或清單。

表格前後請保留空行，不要緊貼標題、圖片或 code block：

```md
判斷標準：

| 狀態 | 是否可繼續 | 說明 |
|---|---|---|
| green | 可以 | primary / replica 都正常 |
| yellow | POC 可繼續 | single node 常見狀態 |
| red | 不建議繼續 | 需先修復 primary shard |

後續說明文字。
```

## 圖片規則

為避免圖片被 Pandoc 當成 implicit figure，圖片請使用空 alt，圖說另起一行：

```md
![](images/example.png)

▲ 圖：圖片說明
```

圖片前後請保留空行，不要緊貼標題、表格、code block 或 `---`。

不要這樣寫：

```md
![圖片說明](images/example.png)
---
```

這種寫法可能讓圖片 caption 或分隔線在 DOCX 目錄與版面中產生非預期結果。

## Placeholder 規則

在 fenced code block 內可以直接保留 placeholder：

````md
```bash
curl -k -u 'elastic:<PASSWORD>' https://<ELK_IP>:9200
```
````

在一般段落、清單或表格中，角括號 placeholder 需跳脫：

```md
- [ ] Fleet Server host = https://\<ELK_IP\>:8220
- [ ] elastic-agent-\<version\>-linux-x86_64.tar.gz
```

或改用全大寫底線格式：

```md
- [ ] Fleet Server host = https://ELK_IP:8220
- [ ] elastic-agent-VERSION-linux-x86_64.tar.gz
```

## Word 目錄規則

CLI 產出的 DOCX 使用 Word 原生目錄。開啟檔案後若目錄頁碼顯示為 `1` 或尚未更新，請在 Word 中更新功能變數：

- 開檔提示更新功能變數時選「是」
- 或點選目錄後使用「更新功能變數」並選「更新整個目錄」
- 或全選文件後按 `F9` / `Fn + F9`

## 交付前自檢

### 共通規則

- [ ] 標題層級沒有跳級
- [ ] 一般說明沒有被包在 `text` code block
- [ ] 整份文件沒有保留外層 `markdown` fenced code block
- [ ] 檢查表皆為 `- [ ]`
- [ ] 指令 code block 有正確語言標籤
- [ ] 表格欄位數一致
- [ ] 表格前後有空行，沒有緊貼標題、圖片或 code block
- [ ] 圖片使用空 alt，圖說另起一行
- [ ] 圖片路徑可被轉換工具讀取
- [ ] 一般段落、清單、表格中的 `<PLACEHOLDER>` 已跳脫或改寫
- [ ] 內容完整，沒有為了排版刪減資訊

### Engineering Note

- [ ] 已記錄問題背景與目前範圍
- [ ] 已區分可驗證事實、推測與目前結論
- [ ] 已記錄判斷依據與決策理由
- [ ] 已記錄執行結果、未完成項目或後續待辦

Engineering Note 不需要通過 Enterprise SOP 專用的操作步驟與交付檢查項目。

### Enterprise SOP

- [ ] 已說明目的、適用範圍與前提條件
- [ ] 操作步驟可由其他人依序執行
- [ ] 每個重要步驟都有預期結果或判斷標準
- [ ] 已記錄驗證方式、常見問題與排錯方法
- [ ] 已記錄風險、限制、收尾檢查與版本資訊
