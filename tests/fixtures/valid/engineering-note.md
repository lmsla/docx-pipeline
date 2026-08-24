---
title: Validator Engineering Note
project: docx-pipeline
document_type: Engineering Note
author: Russell
date: 2026-08-23
status: draft
numbering: engineering
---

# 摘要

這是一份用於驗證 Markdown 結構的工程筆記。

# 背景與問題

需要確認 code block、表格與標題層級可以通過 validator。

## 觀察

```bash
docx-pipeline validate input.md
```

| 項目 | 結果 |
|---|---|
| validator | pass |
