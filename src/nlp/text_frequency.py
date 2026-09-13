#!/usr/bin/env python3

import argparse
import re
from collections import Counter
from pathlib import Path

import jieba


def read_text(path: Path) -> str:
    """读取 UTF-8 文本文件。"""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"错误：文件不存在：{path}")
    except UnicodeDecodeError:
        raise SystemExit(f"错误：无法使用 UTF-8 解码文件：{path}")


def count_characters(text: str) -> Counter[str]:
    """
    统计字频。
    只统计中文字符、英文字母和数字，忽略空格和标点。
    """
    chars = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", text)
    return Counter(chars)


def count_words(text: str) -> Counter[str]:
    """
    使用 jieba 分词并统计词频。
    过滤空白和纯标点。
    """
    words = jieba.cut(text)

    counter = Counter()

    for word in words:
        word = word.strip()

        if not word:
            continue

        # 至少包含中文、英文或数字
        if not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", word):
            continue

        counter[word] += 1

    return counter


def print_frequency(
    title: str,
    counter: Counter[str],
    top: int,
) -> None:
    """格式化输出频率统计。"""
    print()
    print("=" * 40)
    print(title)
    print("=" * 40)
    print(f"{'内容':<16}{'次数':>8}{'频率':>12}")
    print("-" * 40)

    total = sum(counter.values())

    if total == 0:
        print("无可统计内容")
        return

    for item, count in counter.most_common(top):
        frequency = count / total
        print(f"{item:<16}{count:>8}{frequency:>11.2%}")

    print("-" * 40)
    print(f"总计：{total}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取文本文件并统计字频和词频"
    )

    parser.add_argument(
        "file",
        type=Path,
        help="需要分析的文本文件",
    )

    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="显示频率最高的前 N 项，默认 20",
    )

    parser.add_argument(
        "--char-only",
        action="store_true",
        help="只统计字频",
    )

    parser.add_argument(
        "--word-only",
        action="store_true",
        help="只统计词频",
    )

    args = parser.parse_args()

    if args.top <= 0:
        parser.error("--top 必须大于 0")

    if args.char_only and args.word_only:
        parser.error("--char-only 与 --word-only 不能同时使用")

    text = read_text(args.file)

    print(f"文件：{args.file}")
    print(f"字符数：{len(text)}")

    if not args.word_only:
        chars = count_characters(text)
        print_frequency("字频统计", chars, args.top)

    if not args.char_only:
        words = count_words(text)
        print_frequency("词频统计", words, args.top)


if __name__ == "__main__":
    main()