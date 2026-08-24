import tempfile
import unittest
from pathlib import Path

from docx_pipeline.validator import validate_markdown


class ValidatorTest(unittest.TestCase):
    def test_valid_engineering_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "diagram.png").write_bytes(b"png")
            markdown = root / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
author: Russell
date: 2026-08-23
status: draft
---

# 摘要

目前結論。

# 背景與問題

問題描述。

```bash
echo ok
```

| 項目 | 結果 |
|---|---|
| status | green |

![](diagram.png)
""",
                encoding="utf-8",
            )
            self.assertEqual(validate_markdown(markdown), [])

    def test_invalid_document_reports_structure_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
date: 2026-08-23
status: draft
---

# 摘要

### 跳級

```bash
echo missing close
""",
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertIn("MD011", codes)
            self.assertIn("MD031", codes)
            self.assertNotIn("MD040", codes)

    def test_outer_markdown_fence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "wrapped.md"
            markdown.write_text(
                """---
title: 包裝測試
project: 測試專案
document_type: Engineering Note
date: 2026-08-23
status: draft
---

````markdown
# 摘要

目前結論。

```bash
echo ok
```

# 背景與問題

問題描述。
````
""",
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertIn("MD012", codes)


    def test_missing_author_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
date: 2026-08-23
status: draft
---

# 摘要

內容。

# 背景與問題

問題描述。
""",
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertIn("MD005", codes)

    def test_template_placeholder_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
author: 撰寫者姓名
date: 2026-08-23
status: draft
---

# 摘要

內容。

# 背景與問題

問題描述。
""",
                encoding="utf-8",
            )
            issues = validate_markdown(markdown)
            placeholder = [i for i in issues if i.code == "MD009"]
            self.assertTrue(placeholder)
            self.assertIn("author", placeholder[0].message)

    def test_hardcoded_secret_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
author: Russell
date: 2026-08-23
status: draft
---

# 摘要

內容。

# 背景與問題

```bash
curl -u elastic:S3cr3tP4ssw0rd https://es.example.com:9200
export API_KEY=aQ82ndPqR91xLmZ0
```
""",
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertIn("MD063", codes)

    def test_redacted_credentials_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = Path(directory) / "note.md"
            markdown.write_text(
                """---
title: 測試筆記
project: 測試專案
document_type: Engineering Note
author: Russell
date: 2026-08-23
status: draft
---

# 摘要

內容。

# 背景與問題

```bash
curl -u elastic:<ELASTIC_PASSWORD> https://<ELK_IP>:9200
export API_KEY="${ELASTIC_API_KEY}"
```
""",
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertFalse({c for c in codes if c.startswith("MD06")})

    def _identifying_doc(self, directory, distribution):
        markdown = Path(directory) / "note.md"
        markdown.write_text(
            f"""---
title: 測試筆記
project: 範例客戶 POC
document_type: Engineering Note
author: Russell
date: 2026-08-23
status: draft
distribution: {distribution}
---

# 摘要

範例客戶的正式環境 10.20.30.40，窗口 wang@customer.com.tw。

# 背景與問題

問題描述。
""",
            encoding="utf-8",
        )
        (Path(directory) / ".docx-pipeline-denylist").write_text(
            "# 清單\n範例客戶\n", encoding="utf-8"
        )
        return markdown

    def test_identifying_info_allowed_for_internal_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = self._identifying_doc(directory, "internal")
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertFalse({c for c in codes if c in {"MD064", "MD065", "MD066"}})

    def test_identifying_info_rejected_for_external_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = self._identifying_doc(directory, "public")
            codes = {issue.code for issue in validate_markdown(markdown)}
            self.assertIn("MD064", codes)
            self.assertIn("MD065", codes)
            self.assertIn("MD066", codes)

    def test_denylist_matches_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown = self._identifying_doc(directory, "customer")
            hits = [i for i in validate_markdown(markdown) if i.code == "MD064"]
            # project: 範例客戶 POC 位於 frontmatter，必須被涵蓋
            self.assertTrue(any(i.line <= 8 for i in hits))



if __name__ == "__main__":
    unittest.main()
