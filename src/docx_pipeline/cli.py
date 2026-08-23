from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .numbering import PROFILES, number_markdown
from .validator import validate_markdown


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parents[2] / relative_path


def check_pandoc() -> str | None:
    env_pandoc = os.environ.get("DOCX_PIPELINE_PANDOC")
    if env_pandoc and Path(env_pandoc).exists():
        return env_pandoc

    bundled_pandoc = resource_path("bin/pandoc")
    if bundled_pandoc.exists():
        return str(bundled_pandoc)

    return shutil.which("pandoc")


def extract_markdown_metadata(markdown: Path) -> dict[str, str]:
    text = markdown.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}

    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                match = re.match(r"^([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
                if match:
                    metadata[match.group(1).strip()] = match.group(2).strip().strip("\"'")

    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match and "title" not in metadata:
            metadata["title"] = match.group(1).strip()
            break

    metadata.setdefault("title", markdown.stem)
    return metadata


def run_pandoc(markdown: Path, reference_doc: Path, output: Path, toc: bool) -> None:
    pandoc = check_pandoc()
    if pandoc is None:
        raise RuntimeError("Pandoc is not installed and no bundled pandoc was found.")

    cmd = [
        pandoc,
        str(markdown.name),
        "--reference-doc",
        str(reference_doc),
        "-o",
        str(output),
    ]
    if toc:
        cmd[2:2] = ["--toc", "--toc-depth=3", "-M", "toc-title=目錄"]

    try:
        subprocess.run(cmd, check=True, cwd=markdown.parent)
    except FileNotFoundError as exc:
        raise RuntimeError("Pandoc is not installed. Install it with: brew install pandoc") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Pandoc failed with exit code {exc.returncode}") from exc


def build(args: argparse.Namespace) -> int:
    from .postprocess import postprocess_docx

    markdown = Path(args.markdown).expanduser().resolve()
    reference_doc = (
        Path(args.reference_doc).expanduser().resolve()
        if args.reference_doc
        else resource_path("templates/reference.docx")
    )
    output = Path(args.output).expanduser().resolve()
    intermediate = output.with_suffix(".pandoc.docx")

    if not markdown.exists():
        raise RuntimeError(f"Markdown file not found: {markdown}")
    if not reference_doc.exists():
        raise RuntimeError(f"Reference DOCX not found: {reference_doc}")

    output.parent.mkdir(parents=True, exist_ok=True)

    metadata = extract_markdown_metadata(markdown)
    header_text = "" if args.no_header else (args.header or metadata["title"])

    native_toc = not args.no_toc and not args.static_toc
    static_toc = not args.no_toc and args.static_toc

    numbering = args.numbering or metadata.get("numbering")
    numbered_md: Path | None = None
    if numbering:
        if numbering not in PROFILES:
            raise RuntimeError(
                f"unknown numbering profile: {numbering} (expected one of {', '.join(PROFILES)})"
            )
        # 暫存檔必須與來源同目錄，pandoc 才能解析相對圖片路徑
        numbered_md = markdown.parent / f".{markdown.stem}.numbered.md"
        numbered_md.write_text(
            number_markdown(markdown.read_text(encoding="utf-8"), numbering),
            encoding="utf-8",
        )

    try:
        run_pandoc(numbered_md or markdown, reference_doc, intermediate, toc=native_toc)
    finally:
        if numbered_md is not None and not args.keep_intermediate:
            numbered_md.unlink(missing_ok=True)
    postprocess_docx(
        intermediate,
        output,
        header_text=header_text,
        metadata=metadata,
        add_cover=not args.no_cover,
        add_toc=static_toc,
        clear_dirty_fields=not native_toc,
        normalize_tables=not args.no_table_cleanup,
        normalize_images=not args.no_image_cleanup,
        chapter_page_breaks=not args.no_chapter_breaks,
    )

    if not args.keep_intermediate:
        intermediate.unlink(missing_ok=True)

    print(f"Wrote {output}")
    return 0


def doctor(_: argparse.Namespace) -> int:
    pandoc = check_pandoc()
    if pandoc:
        print(f"pandoc: {pandoc}")
    else:
        print("pandoc: missing (install with: brew install pandoc)")

    try:
        import docx  # noqa: F401

        print("python-docx: installed")
    except ModuleNotFoundError:
        print("python-docx: missing (install with: pip install python-docx)")

    return 0


def validate(args: argparse.Namespace) -> int:
    markdown = Path(args.markdown).expanduser().resolve()
    if not markdown.exists():
        raise RuntimeError(f"Markdown file not found: {markdown}")

    try:
        issues = validate_markdown(markdown, document_type=args.document_type)
    except OSError as exc:
        raise RuntimeError(f"Cannot read Markdown file: {markdown}: {exc}") from exc
    for issue in issues:
        print(f"{issue.code}: {markdown}:{issue.line}: {issue.message}", file=sys.stderr)
    if issues:
        print(f"Validation failed: {len(issues)} issue(s).", file=sys.stderr)
        return 1

    print(f"Valid Markdown: {markdown}")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docx-pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Convert Markdown to enterprise DOCX")
    build_parser.add_argument("markdown", help="Input Markdown file")
    build_parser.add_argument("-o", "--output", required=True, help="Output DOCX file")
    build_parser.add_argument(
        "--reference-doc",
        default=None,
        help="Pandoc reference DOCX template",
    )
    build_parser.add_argument(
        "--header",
        default=None,
        help="Header text for all sections. Defaults to Markdown title.",
    )
    build_parser.add_argument("--no-header", action="store_true", help="Do not write a header")
    build_parser.add_argument(
        "--numbering",
        default=None,
        choices=list(PROFILES),
        help="Heading numbering profile. Falls back to frontmatter 'numbering:'; omit to disable.",
    )
    build_parser.add_argument("--no-cover", action="store_true", help="Skip generated cover page")
    build_parser.add_argument("--no-toc", action="store_true", help="Skip table of contents generation")
    build_parser.add_argument("--static-toc", action="store_true", help="Use static TOC without page numbers")
    build_parser.add_argument("--keep-intermediate", action="store_true", help="Keep the Pandoc DOCX before cleanup")
    build_parser.add_argument("--no-table-cleanup", action="store_true", help="Skip table normalization")
    build_parser.add_argument("--no-image-cleanup", action="store_true", help="Skip image normalization")
    build_parser.add_argument("--no-chapter-breaks", action="store_true", help="Skip page breaks before Heading 1")
    build_parser.set_defaults(func=build)

    doctor_parser = subparsers.add_parser("doctor", help="Check local dependencies")
    doctor_parser.set_defaults(func=doctor)

    validate_parser = subparsers.add_parser("validate", help="Validate Markdown structure and assets")
    validate_parser.add_argument("markdown", help="Input Markdown file")
    validate_parser.add_argument(
        "--type",
        dest="document_type",
        choices=("engineering-note", "enterprise-sop"),
        default=None,
        help="Document type override when frontmatter document_type is unavailable or custom",
    )
    validate_parser.set_defaults(func=validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
