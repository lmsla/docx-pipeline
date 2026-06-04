# AI Agent Markdown 寫作規則

請依照以下規則撰寫筆記、SOP 或交付文件。目標是讓 Markdown 可讀、可維護，並能穩定轉換成企業格式 DOCX。

## 核心原則

- 內容必須完整保留，不得為了排版刪減技術細節。
- 使用標準 Markdown 語義，不要用 code block 假裝排版。
- 文件標題與 metadata 放在 YAML front matter。
- 章節從 `#` 開始，子章節依序使用 `##`、`###`、`####`。
- 不要跳級使用標題，例如 `#` 後直接接 `###`。
- 指令、設定檔、HTTP request、JSON、YAML、原始輸出才使用 fenced code block。
- 一般說明、注意事項、判斷原則、前提條件請使用段落或清單。
- 檢查表使用 `- [ ]`，不要寫成 `[ ]`，也不要包在 code block。
- 流程步驟使用真正的 numbered list。
- 可比較資料使用表格，不要用空白對齊文字。
- 一般段落或清單中的 placeholder 若使用角括號，需跳脫成 `\<ELK_IP\>`，避免被 Markdown 轉換器視為 HTML tag。
- 不要在章節之間用 `---` 當視覺分隔，DOCX 轉換時會由標題、段落間距與頁面樣式處理區隔。

## 建議文件結構

```md
---
title: 文件標題
project: 專案名稱
document_type: SOP
version: 1.0
date: YYYY-MM-DD
owner: 撰寫人或負責單位
audience: 客戶 / 主管 / 維運人員 / 開發人員
status: draft
---

# 文件標題

## 0. 文件目的

# 1. 整體流程

# 2. 準備事項

# 3. 操作步驟

# 4. 驗證方式

# 5. 常見問題與排錯

# 6. 收尾檢查

# 7. 風險與限制

# 8. 待辦事項

# 9. 附錄
```

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

- [ ] 標題層級沒有跳級
- [ ] 一般說明沒有被包在 `text` code block
- [ ] 檢查表皆為 `- [ ]`
- [ ] 指令 code block 有正確語言標籤
- [ ] 表格欄位數一致
- [ ] 表格前後有空行，沒有緊貼標題、圖片或 code block
- [ ] 圖片使用空 alt，圖說另起一行
- [ ] 圖片路徑可被轉換工具讀取
- [ ] 一般段落、清單、表格中的 `<PLACEHOLDER>` 已跳脫或改寫
- [ ] 內容完整，沒有為了排版刪減資訊
