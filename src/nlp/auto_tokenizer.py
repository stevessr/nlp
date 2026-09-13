#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer

DEFAULT_MODEL = "bert-base-chinese"


def read_text(path: Path) -> str:
    """读取 UTF-8 文本文件。"""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"错误：文件不存在：{path}")
    except UnicodeDecodeError:
        raise SystemExit(f"错误：无法使用 UTF-8 解码文件：{path}")


def load_tokenizer(model: str, *, local_files_only: bool = False) -> Any:
    """加载 tokenizer，并可选择强制只使用本地文件。

    ``local_files_only`` 让 CLI 可以在离线环境中运行：传入的 ``model``
    可以是本地 tokenizer 目录，也可以是已经存在于 Hugging Face 缓存中的
    模型名称；缺少文件时会立即报错，而不是尝试联网下载。
    """
    options: dict[str, Any] = {}
    if local_files_only:
        options["local_files_only"] = True

    try:
        return AutoTokenizer.from_pretrained(model, **options)
    except (OSError, ValueError) as exc:
        if local_files_only:
            source_hint = "本地 tokenizer 目录或本地缓存"
        else:
            source_hint = "模型名称、网络连接或本地缓存"

        raise SystemExit(
            f"错误：无法加载 tokenizer「{model}」。"
            f"请检查{source_hint}。"
            f"\n详细信息：{exc}"
        ) from exc


def tokenize_text(
    tokenizer: Any,
    text: str,
    *,
    add_special_tokens: bool = True,
    max_length: int | None = None,
) -> dict[str, Any]:
    """使用 tokenizer 编码文本并整理 CLI 输出所需的字段。"""
    if max_length is not None and max_length <= 0:
        raise ValueError("max_length must be greater than 0")

    options: dict[str, Any] = {
        "add_special_tokens": add_special_tokens,
        "return_attention_mask": True,
    }

    if max_length is not None:
        options.update(truncation=True, max_length=max_length)

    encoded = tokenizer(text, **options)
    input_ids = encoded["input_ids"]

    return {
        "tokens": tokenizer.convert_ids_to_tokens(input_ids),
        "input_ids": input_ids,
        "attention_mask": encoded.get("attention_mask", []),
        "token_count": len(input_ids),
    }


def build_parser() -> argparse.ArgumentParser:
    """构造 AutoTokenizer 命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="使用 Hugging Face AutoTokenizer 生成文本 token 和 token ID"
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="需要编码的文本；也可以使用 --file 从文件读取",
    )

    parser.add_argument(
        "--file",
        type=Path,
        help="读取 UTF-8 文本文件作为输入",
    )

    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"Hugging Face 模型或 tokenizer 名称，默认 {DEFAULT_MODEL}",
    )

    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="只使用本地 tokenizer 目录或缓存，不访问 Hugging Face",
    )

    parser.add_argument(
        "--max-length",
        type=int,
        help="截断后的最大 token 数量；不指定时不截断",
    )

    parser.add_argument(
        "--no-special-tokens",
        action="store_true",
        help="不加入模型的特殊 token，例如 [CLS] 和 [SEP]",
    )

    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="以 JSON 格式输出结果",
    )

    return parser


def print_result(result: dict[str, Any], *, json_output: bool) -> None:
    """以人类可读或 JSON 格式输出编码结果。"""
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"模型：{result['model']}")
    print(f"文本：{result['text']}")
    print(f"Token 数量：{result['token_count']}")
    print()
    print("Tokens:")
    for index, token in enumerate(result["tokens"]):
        print(f"  {index}: {token}")
    print()
    print(f"input_ids:{result['input_ids']}")
    print(f"attention_mask:{result['attention_mask']}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if (args.text is None) == (args.file is None):
        parser.error("必须且只能提供文本参数或 --file")

    if args.max_length is not None and args.max_length <= 0:
        parser.error("--max-length 必须大于 0")

    text = read_text(args.file) if args.file is not None else args.text

    tokenizer = load_tokenizer(
        args.model,
        local_files_only=args.local_files_only,
    )

    tokenized = tokenize_text(
        tokenizer,
        text,
        add_special_tokens=not args.no_special_tokens,
        max_length=args.max_length,
    )
    result = {
        "model": args.model,
        "text": text,
        **tokenized,
    }
    print_result(result, json_output=args.json_output)


if __name__ == "__main__":
    main()
