from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urlparse

from .numbering import HEADING_RE


DOCUMENT_TYPES = {
    "engineering-note": {
        "required_fields": (),
        "required_headings": ("摘要", "背景與問題"),
    },
    "enterprise-sop": {
        "required_fields": ("version", "owner", "audience", "numbering"),
        "required_headings": ("文件說明", "前提條件", "操作步驟", "驗證方式", "風險與限制"),
    },
}

FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")
FENCE_LINE_RE = re.compile(r"^\s{0,3}([`~]{3,})(.*)$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)")
PLACEHOLDER_RE = re.compile(r"(?<!\\)<([A-Za-z][A-Za-z0-9_.:-]{2,})>")
MANUAL_NUMBER_RE = re.compile(r"^(?:\d+(?:\.\d+)*、\s*|\d+(?:\.\d+)*\.\s+|\d+(?:\.\d+)+\s+)")
COMMON_HTML_TAGS = {"a", "br", "code", "div", "em", "img", "li", "ol", "p", "pre", "span", "strong", "ul"}

# 模板原樣未填的佔位值。留著這些值等於沒有填寫，對追溯與交付都無效。
TEMPLATE_PLACEHOLDERS = {
    "撰寫者姓名",
    "撰寫人或負責單位",
    "負責單位或維護者",
    "文件標題",
    "技術筆記標題",
    "專案名稱",
    "yyyy-mm-dd",
    "tbd",
    "todo",
    "unknown",
    "n/a",
    "na",
    "-",
}


# 憑證偵測。刻意採高精確度樣式，寧可漏報也不要誤擋合法的技術內容——
# 語意層的客戶名、主機名判斷交給 Skill 與人工複核，validator 只抓機器可確認的部分。
PRIVATE_KEY_RE = re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----")
AWS_ACCESS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}")
SECRET_ASSIGN_RE = re.compile(
    r"\b(password|passwd|pwd|token|api[_-]?key|apikey|secret|access[_-]?key|client[_-]?secret)"
    r"\s*[:=]\s*[\"']?([^\s\"',;]{8,})",
    re.IGNORECASE,
)
# curl -u user:pass 這類把帳密寫進指令的寫法
CURL_USERPASS_RE = re.compile(r"-[uU]\s+[^\s:]+:([^\s\"']{4,})")

# 已去識別化的值不該被當成外洩。涵蓋角括號 placeholder、遮罩、環境變數與明顯的範例值。
REDACTED_HINTS = (
    "<", ">", "***", "xxx", "your", "changeme", "change_me", "redacted", "example",
    "placeholder", "dummy", "sample", "${", "{{", "%s", "...", "____",
)


def _looks_redacted(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in REDACTED_HINTS)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    line: int
    message: str


def _issue(code: str, line: int, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, line=line, message=message)


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int, list[ValidationIssue]]:
    metadata: dict[str, str] = {}
    issues: list[ValidationIssue] = []

    if not lines or lines[0].strip() != "---":
        return metadata, 0, [_issue("MD001", 1, "frontmatter 必須從第一行的 --- 開始")]

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            end = index
            break

    if end is None:
        return metadata, len(lines), [_issue("MD002", 1, "frontmatter 缺少結尾的 --- 或 ...")]

    for index, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = FRONTMATTER_KEY_RE.match(line)
        if not match:
            issues.append(_issue("MD003", index, "frontmatter 只支援單行 key: value 格式"))
            continue
        key, value = match.groups()
        if key in metadata:
            issues.append(_issue("MD004", index, f"frontmatter 欄位重複：{key}"))
        metadata[key] = value.strip().strip("\"'")

    return metadata, end + 1, issues


def _document_type(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    if normalized in {"engineering", "engineering-note", "note"}:
        return "engineering-note"
    if normalized in {"sop", "enterprise-sop", "enterprise-sop-template"}:
        return "enterprise-sop"
    return None


def _heading_name(title: str) -> str:
    title = re.sub(r"<!--.*?-->", "", title).strip()
    return MANUAL_NUMBER_RE.sub("", title).strip()


def _scan_outer_document_fence(lines: list[str], start: int) -> list[ValidationIssue]:
    """Reject chat transport wrappers that were accidentally saved in the Markdown file."""
    content_indices = [index for index in range(start, len(lines)) if lines[index].strip()]
    if len(content_indices) < 2:
        return []

    opening_index = content_indices[0]
    closing_index = content_indices[-1]
    opening_match = FENCE_LINE_RE.match(lines[opening_index])
    closing_match = FENCE_LINE_RE.match(lines[closing_index])
    if not opening_match or not closing_match:
        return []

    opening_token, opening_remainder = opening_match.groups()
    closing_token, closing_remainder = closing_match.groups()
    language = opening_remainder.strip().split(None, 1)[0].lower() if opening_remainder.strip() else ""
    if language not in {"md", "markdown"}:
        return []
    if opening_token[0] != closing_token[0] or len(closing_token) < len(opening_token):
        return []
    if closing_remainder.strip():
        return []

    return [
        _issue(
            "MD012",
            opening_index + 1,
            "整份 Markdown 不應包在外層 fenced code block；存檔前請移除 ```markdown 包裝",
        )
    ]


def _scan_fences(lines: list[str], start: int) -> tuple[set[int], list[ValidationIssue]]:
    code_lines: set[int] = set()
    issues: list[ValidationIssue] = []
    opening_line = 0
    opening_char = ""
    opening_length = 0

    for index in range(start, len(lines)):
        line_number = index + 1
        match = FENCE_LINE_RE.match(lines[index])
        if not match:
            if opening_char:
                code_lines.add(index)
            continue

        token, remainder = match.groups()
        char = token[0]
        if not opening_char:
            language = remainder.strip().split(None, 1)[0] if remainder.strip() else ""
            if not language:
                issues.append(_issue("MD010", line_number, "fenced code block 必須標示語言，例如 ```bash 或 ```text"))
            opening_line = line_number
            opening_char = char
            opening_length = len(token)
            continue

        if char == opening_char and len(token) >= opening_length and not remainder.strip():
            opening_char = ""
            opening_length = 0
            opening_line = 0
            continue
        code_lines.add(index)

    if opening_char:
        issues.append(_issue("MD011", opening_line, "fenced code block 沒有關閉標記"))

    return code_lines, issues


def _split_table_cells(line: str) -> list[str]:
    content = line.strip()
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|") and not content.endswith("\\|"):
        content = content[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    inline_code = False
    for char in content:
        if char == "`" and not escaped:
            inline_code = not inline_code
        if char == "|" and not escaped and not inline_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).strip())
    return cells


def _is_table_separator(line: str) -> bool:
    cells = _split_table_cells(line)
    return len(cells) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _scan_tables(lines: list[str], start: int, code_lines: set[int]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    index = start
    while index + 1 < len(lines):
        if index in code_lines or index + 1 in code_lines:
            index += 1
            continue
        header = lines[index]
        separator = lines[index + 1]
        if "|" not in header or not _is_table_separator(separator):
            index += 1
            continue

        expected = len(_split_table_cells(header))
        actual_separator = len(_split_table_cells(separator))
        if expected != actual_separator:
            issues.append(
                _issue(
                    "MD020",
                    index + 2,
                    f"表格分隔列數 {actual_separator} 與表頭欄數 {expected} 不一致",
                )
            )

        index += 2
        while index < len(lines):
            if index in code_lines or not lines[index].strip() or "|" not in lines[index]:
                break
            actual = len(_split_table_cells(lines[index]))
            if actual != expected:
                issues.append(
                    _issue(
                        "MD021",
                        index + 1,
                        f"表格資料列欄數 {actual} 與表頭欄數 {expected} 不一致",
                    )
                )
            index += 1
    return issues


def _scan_structure(
    lines: list[str], start: int, code_lines: set[int]
) -> tuple[list[tuple[int, str]], list[ValidationIssue]]:
    headings: list[tuple[int, str]] = []
    issues: list[ValidationIssue] = []
    previous_level = 0

    for index in range(start, len(lines)):
        if index in code_lines:
            continue
        match = HEADING_RE.match(lines[index])
        if not match:
            continue
        level = len(match.group(1))
        name = _heading_name(match.group(2))
        if not headings and level != 1:
            issues.append(_issue("MD030", index + 1, "文件正文的第一個標題必須是 H1"))
        if previous_level and level > previous_level + 1:
            issues.append(
                _issue(
                    "MD031",
                    index + 1,
                    f"標題層級不可跳級：H{previous_level} 後不能直接使用 H{level}",
                )
            )
        headings.append((level, name))
        previous_level = level

    if not headings:
        issues.append(_issue("MD032", start + 1, "文件至少需要一個 H1 標題"))
    return headings, issues


def _scan_images_and_placeholders(
    lines: list[str], start: int, code_lines: set[int], markdown: Path
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for index in range(start, len(lines)):
        if index in code_lines:
            continue
        line = re.sub(r"<!--.*?-->", "", lines[index])
        for match in IMAGE_RE.finditer(line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            parsed = urlparse(target)
            if parsed.scheme.lower() in {"data", "http", "https"} or target.startswith("//"):
                continue
            image_path = (markdown.parent / target).resolve()
            if not image_path.is_file():
                issues.append(_issue("MD040", index + 1, f"圖片檔案不存在：{target}"))
        placeholder = next(
            (
                match
                for match in PLACEHOLDER_RE.finditer(line)
                if match.group(1).lower() not in COMMON_HTML_TAGS
                and (
                    match.group(1).isupper()
                    or "_" in match.group(1)
                    or match.group(1).lower() in {"hostname", "ip", "password", "url", "username", "version"}
                )
            ),
            None,
        )
        if placeholder:
            issues.append(_issue("MD050", index + 1, "一般文字中的 placeholder 必須跳脫角括號，例如 \\<ELK_IP\\>"))
    return issues


def _scan_secrets(lines: list[str], start: int) -> list[ValidationIssue]:
    """偵測寫死的憑證。

    與其他檢查不同，這裡**不跳過 fenced code block**——指令與設定範例正是憑證最常
    出現的地方。已用 placeholder 或環境變數遮蔽的值不視為外洩。
    """
    issues: list[ValidationIssue] = []
    for index in range(start, len(lines)):
        line = lines[index]
        line_number = index + 1

        if PRIVATE_KEY_RE.search(line):
            issues.append(_issue("MD060", line_number, "文件內含私鑰內容，請移除並改以安全管道傳遞"))
            continue

        match = AWS_ACCESS_KEY_RE.search(line)
        if match:
            issues.append(_issue("MD061", line_number, f"疑似 AWS access key ID：{match.group(0)}"))
            continue

        if BEARER_RE.search(line):
            issues.append(_issue("MD062", line_number, "文件內含 Bearer token，請以 \\<TOKEN\\> 之類的 placeholder 取代"))
            continue

        match = SECRET_ASSIGN_RE.search(line)
        if match and not _looks_redacted(match.group(2)):
            issues.append(
                _issue("MD063", line_number, f"疑似寫死的憑證：{match.group(1)} 的值請改為 placeholder")
            )
            continue

        match = CURL_USERPASS_RE.search(line)
        if match and not _looks_redacted(match.group(1)):
            issues.append(
                _issue("MD063", line_number, "指令中含明文帳號密碼，請改用 placeholder 或改從環境變數讀取")
            )

    return issues


def validate_markdown(markdown: Path, document_type: str | None = None) -> list[ValidationIssue]:
    try:
        text = markdown.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [_issue("MD000", 1, "Markdown 必須使用 UTF-8 編碼")]

    lines = text.splitlines()
    metadata, body_start, issues = _parse_frontmatter(lines)
    required_fields = ("title", "project", "document_type", "author", "date", "status")
    for field in required_fields:
        if not metadata.get(field):
            issues.append(_issue("MD005", 1, f"frontmatter 缺少必要欄位：{field}"))

    for field, value in metadata.items():
        if value.strip().lower() in TEMPLATE_PLACEHOLDERS:
            issues.append(
                _issue(
                    "MD009",
                    1,
                    f"frontmatter 欄位 {field} 仍是模板佔位值「{value.strip()}」，請填入實際內容",
                )
            )

    selected_type = document_type or _document_type(metadata.get("document_type"))
    if selected_type is None:
        issues.append(
            _issue(
                "MD006",
                1,
                "無法判斷文件類型；請使用 document_type: Engineering Note/SOP 或 --type",
            )
        )
    else:
        for field in DOCUMENT_TYPES[selected_type]["required_fields"]:
            if not metadata.get(field):
                issues.append(_issue("MD007", 1, f"{selected_type} 缺少必要欄位：{field}"))

    issues.extend(_scan_outer_document_fence(lines, body_start))
    code_lines, fence_issues = _scan_fences(lines, body_start)
    issues.extend(fence_issues)
    headings, structure_issues = _scan_structure(lines, body_start, code_lines)
    issues.extend(structure_issues)
    issues.extend(_scan_tables(lines, body_start, code_lines))
    issues.extend(_scan_images_and_placeholders(lines, body_start, code_lines, markdown))
    issues.extend(_scan_secrets(lines, body_start))

    if selected_type is not None:
        heading_names = {name for _, name in headings}
        for required_heading in DOCUMENT_TYPES[selected_type]["required_headings"]:
            if required_heading not in heading_names:
                issues.append(_issue("MD008", 1, f"{selected_type} 缺少必要章節：{required_heading}"))

    return issues
