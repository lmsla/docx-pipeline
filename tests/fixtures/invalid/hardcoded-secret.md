---
title: 憑證外洩測試
project: 測試專案
document_type: Engineering Note
author: Russell
date: 2026-08-24
status: draft
---

# 摘要

指令中寫死密碼，應被 MD063 擋下。

# 背景與問題

```bash
curl -u elastic:S3cr3tP4ssw0rd https://es.example.com:9200
```
