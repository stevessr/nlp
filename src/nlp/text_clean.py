#!/usr/bin/env python3

import argparse
import re
import sys
import unicodedata
from pathlib import Path

URL_RE = re.compile(
    r"(?i)\b(?:https?://|www\.)[a-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+"
)
NORMALIZATION_FORMS = ("NFC", "NFKC", "NFD", "NFKD")


def _replace_unicode_categories(text: str, prefixes: tuple[str, ...]) -> str:
    """将指定 Unicode 类别的字符替换为空格，避免相邻词被直接拼接。"""
    return "".join(
        " " if unicodedata.category(char).startswith(prefixes) else char
        for char in text
    )


def clean_text(
    text: str,
    *,
    lower: bool = False,
    remove_urls: bool = False,
    remove_numbers: bool = False,
    remove_punctuation: bool = False,
    collapse_whitespace: bool = True,
    remove_blank_lines: bool = True,
    unicode_normalization: str | None = "NFKC",
) -> str:
    """清理文本并返回结果。

    默认执行 NFKC Unicode 规范化、压缩行内空白并删除空行。URL、数字、
    标点和大小写转换均为显式可选项，避免默认清理破坏原始语义。
    """
    if unicode_normalization is not None:
        if unicode_normalization not in NORMALIZATION_FORMS:
            raise ValueError(
                "unicode_normalization must be one of "
                f"{', '.join(NORMALIZATION_FORMS)} or None"
            )
        text = unicodedata.normalize(unicode_normalization, text)

    # 统一换行符，便于后续逐行处理。
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if remove_urls:
        text = URL_RE.sub(" ", text)

    if remove_numbers:
        text = _replace_unicode_categories(text, ("N",))

    if remove_punctuation:
        text = _replace_unicode_categories(text, ("P",))

    if lower:
        text = text.lower()

    lines = text.split("\n")

    if collapse_whitespace:
        lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in lines]

    if remove_blank_lines:
        lines = [line for line in lines if line.strip()]

    return "\n".join(lines)


def read_text(source: str) -> str:
    """从 UTF-8 文件或标准输入读取文本。"""
    if source == "-":
        return sys.stdin.read()

    path = Path(source)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"错误：文件不存在：{path}") from exc
    except UnicodeDecodeError as exc:
        raise SystemExit(f"错误：无法使用 UTF-8 解码文件：{path}") from exc


def write_text(text: str, output: Path | None) -> None:
    """将结果写入 UTF-8 文件；未指定输出文件时写到标准输出。"""
    if output is None:
        sys.stdout.write(text)
        return

    try:
        output.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"错误：无法写入文件：{output}\n详细信息：{exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="清理 UTF-8 文本，支持 Unicode 规范化、URL/数字/标点移除和空白整理"
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="输入文件；省略或使用 - 时从标准输入读取",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="输出文件；默认写到标准输出",
    )
    parser.add_argument("--lower", action="store_true", help="将文本转换为小写")
    parser.add_argument("--remove-urls", action="store_true", help="移除 http(s):// 和 www. URL")
    parser.add_argument("--remove-numbers", action="store_true", help="移除 Unicode 数字字符")
    parser.add_argument("--remove-punctuation", action="store_true", help="移除 Unicode 标点字符")
    parser.add_argument(
        "--keep-whitespace",
        action="store_true",
        help="保留行内连续空白；默认会压缩为空格并去除行首尾空白",
    )
    parser.add_argument(
        "--keep-blank-lines",
        action="store_true",
        help="保留空行；默认删除空行",
    )
    parser.add_argument(
        "--normalize",
        choices=(*NORMALIZATION_FORMS, "none"),
        default="NFKC",
        help="Unicode 规范化形式，默认 NFKC；使用 none 禁用",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    text = read_text(args.file)
    cleaned = clean_text(
        text,
        lower=args.lower,
        remove_urls=args.remove_urls,
        remove_numbers=args.remove_numbers,
        remove_punctuation=args.remove_punctuation,
        collapse_whitespace=not args.keep_whitespace,
        remove_blank_lines=not args.keep_blank_lines,
        unicode_normalization=None if args.normalize == "none" else args.normalize,
    )
    write_text(cleaned, args.output)


if __name__ == "__main__":
    main()
