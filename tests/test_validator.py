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


if __name__ == "__main__":
    unittest.main()
