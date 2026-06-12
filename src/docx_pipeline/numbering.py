from __future__ import annotations

import re

PROFILES = ("engineering", "deliverable-zh")

NO_NUMBER_MARKER = re.compile(r"\s*<!--\s*no-number\s*-->\s*")
APPENDIX_MARKER = re.compile(r"\s*<!--\s*appendix\s*-->\s*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")

# 手寫編號剝除規則（保守判定，避免誤傷「153 主機重建」這類標題）：
# - `1. ` ：數字 + 點 + 空格 → 是編號
# - `2、`：數字 + 頓號（空格可省，中文習慣）→ 是編號
# - `1.1 ` / `2.4.3 `：多段點分式 + 空格 → 是編號
# - `153 主機重建` / `2024 年度回顧` / `1.5G 網路`：無編號標點或無空格邊界 → 標題內容，不剝
MANUAL_NUMBER_RE = re.compile(r"^(?:\d+(?:\.\d+)*、\s*|\d+(?:\.\d+)*\.\s+|\d+(?:\.\d+)+\s+)")

CHINESE_DIGITS = "零一二三四五六七八九"


def to_chinese_numeral(n: int) -> str:
    if n < 0 or n > 99:
        raise ValueError(f"chapter number out of range (1-99): {n}")
    if n < 10:
        return CHINESE_DIGITS[n]
    tens, ones = divmod(n, 10)
    if tens == 1:
        return "十" + (CHINESE_DIGITS[ones] if ones else "")
    return CHINESE_DIGITS[tens] + "十" + (CHINESE_DIGITS[ones] if ones else "")


def appendix_letter(n: int) -> str:
    if n < 1 or n > 26:
        raise ValueError(f"appendix number out of range (1-26): {n}")
    return chr(ord("A") + n - 1)


def format_number(profile: str, counters: list[int], level: int, appendix: int | None) -> str:
    """組合指定層級的編號前綴（含結尾分隔，直接拼在標題文字前）。"""
    if appendix is not None:
        # 附錄：H1 = 附錄 A，子層 = A.1 / A.1.1
        if level == 1:
            return f"附錄 {appendix_letter(appendix)}　"
        sub = ".".join(str(c) for c in counters[1:level])
        return f"{appendix_letter(appendix)}.{sub}　"

    if profile == "deliverable-zh":
        if level == 1:
            return f"第{to_chinese_numeral(counters[0])}章　"
        return ".".join(str(c) for c in counters[:level]) + "　"

    # engineering
    if level == 1:
        return f"{counters[0]}. "
    return ".".join(str(c) for c in counters[:level]) + " "


def number_markdown(text: str, profile: str) -> str:
    """為 Markdown 標題注入章節編號。

    - 跳過 YAML frontmatter 與 fenced code block 內的行
    - 標題開頭的手寫編號（`1.`、`1.1`）會先剝除再重編，
      源文件編號跳號或重複時以實際結構為準自動修正
    - `<!-- no-number -->` 標記的標題不編號（標記會移除）
    - `<!-- appendix -->` 標記的 H1 進入附錄模式（A、B、C…）
    """
    if profile not in PROFILES:
        raise ValueError(f"unknown numbering profile: {profile} (expected one of {PROFILES})")

    lines = text.splitlines(keepends=True)
    out: list[str] = []

    idx = 0
    # 跳過 frontmatter
    if lines and lines[0].strip() == "---":
        out.append(lines[0])
        idx = 1
        while idx < len(lines):
            out.append(lines[idx])
            if lines[idx].strip() in ("---", "..."):
                idx += 1
                break
            idx += 1

    counters = [0] * 6
    appendix_count = 0
    in_appendix = False
    in_fence = False
    fence_token = ""

    for line in lines[idx:]:
        fence_match = FENCE_RE.match(line)
        if fence_match:
            token = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_token = token
            elif token == fence_token:
                in_fence = False
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        heading = HEADING_RE.match(line)
        if not heading:
            out.append(line)
            continue

        level = len(heading.group(1))
        title = MANUAL_NUMBER_RE.sub("", heading.group(2))

        if NO_NUMBER_MARKER.search(title):
            title = NO_NUMBER_MARKER.sub("", title).strip()
            out.append(f"{heading.group(1)} {title}\n")
            continue

        is_appendix_start = bool(APPENDIX_MARKER.search(title))
        if is_appendix_start:
            title = APPENDIX_MARKER.sub("", title).strip()

        if level == 1:
            if is_appendix_start:
                in_appendix = True
                appendix_count += 1
                counters = [0] * 6
            else:
                in_appendix = False
                counters[0] += 1
            for i in range(1, 6):
                counters[i] = 0
        else:
            counters[level - 1] += 1
            for i in range(level, 6):
                counters[i] = 0

        prefix = format_number(
            profile, counters, level, appendix_count if in_appendix else None
        )
        out.append(f"{heading.group(1)} {prefix}{title}\n")

    return "".join(out)
