#!/usr/bin/env python3

from __future__ import annotations

import importlib
import sys
import traceback

RESULTS: list[tuple[str, str, str]] = []


def section(index: int, name: str) -> None:
    print(f"\n[{index}] {name}")


def passed(name: str, message: str = "") -> None:
    RESULTS.append((name, "PASS", message))
    print(f"✓ PASS: {message or name}")


def skipped(name: str, message: str) -> None:
    RESULTS.append((name, "SKIP", message))
    print(f"○ SKIP: {message}")


def failed(name: str, exc: BaseException) -> None:
    RESULTS.append((name, "FAIL", f"{type(exc).__name__}: {exc}"))
    print(f"✗ FAIL: {type(exc).__name__}: {exc}")


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def nltk_resource_exists(path: str) -> bool:
    import nltk

    try:
        nltk.data.find(path)
        return True
    except LookupError:
        return False


print("=" * 60)
print("NLP environment smoke test")
print(f"Python: {sys.version.split()[0]}")
print("=" * 60)


# ============================================================
# 1. NLTK
# ============================================================

section(1, "NLTK")

try:
    import nltk

    print("version:", nltk.__version__)

    # --------------------------------------------------------
    # word_tokenize
    # 新版 NLTK 使用 punkt_tab
    # --------------------------------------------------------

    if nltk_resource_exists("tokenizers/punkt_tab/english/"):
        try:
            from nltk.tokenize import word_tokenize

            text_en = "Natural language processing is very interesting."
            tokens = word_tokenize(text_en)

            print("tokens :", tokens)
            passed("NLTK/tokenizer")
        except Exception as exc:
            failed("NLTK/tokenizer", exc)
    else:
        skipped(
            "NLTK/tokenizer",
            "punkt_tab not downloaded "
            "(run: uv run python -m nltk.downloader punkt_tab)",
        )

    # --------------------------------------------------------
    # stopwords
    # --------------------------------------------------------

    if nltk_resource_exists("corpora/stopwords"):
        try:
            from nltk.corpus import stopwords

            words = stopwords.words("english")

            print("stopwords sample:", words[:10])
            passed("NLTK/stopwords")
        except Exception as exc:
            failed("NLTK/stopwords", exc)
    else:
        skipped(
            "NLTK/stopwords",
            "stopwords not downloaded "
            "(run: uv run python -m nltk.downloader stopwords)",
        )

    passed("NLTK/import", f"NLTK {nltk.__version__}")

except Exception as exc:
    failed("NLTK/import", exc)


# ============================================================
# 2. jieba
# ============================================================

section(2, "jieba")

try:
    import jieba

    text_zh = "华南师范大学计算机学院正在研究自然语言处理和人工智能。"
    tokens = list(jieba.cut(text_zh))

    print("version:", getattr(jieba, "__version__", "unknown"))
    print("tokens :", tokens)

    passed(
        "jieba",
        f"jieba {getattr(jieba, '__version__', 'unknown')}",
    )

except Exception as exc:
    failed("jieba", exc)


# ============================================================
# 3. spaCy
# ============================================================

section(3, "spaCy")

try:
    import spacy

    print("version:", spacy.__version__)

    # blank("zh") 不依赖额外语言模型下载
    nlp = spacy.blank("zh")
    doc = nlp("自然语言处理是人工智能的重要研究方向。")

    print("tokens :", [token.text for token in doc])

    passed("spaCy", f"spaCy {spacy.__version__}")

except Exception as exc:
    failed("spaCy", exc)


# ============================================================
# 4. gensim
# ============================================================

section(4, "gensim")

try:
    import gensim
    from gensim.models import Word2Vec

    sentences = [
        ["自然", "语言", "处理"],
        ["机器", "学习", "人工智能"],
        ["自然", "语言", "人工智能"],
    ]

    model = Word2Vec(
        sentences,
        vector_size=10,
        min_count=1,
        workers=1,
        epochs=10,
    )

    print("version:", gensim.__version__)
    print("vector shape:", model.wv["自然"].shape)

    passed("gensim", f"gensim {gensim.__version__}")

except Exception as exc:
    failed("gensim", exc)


# ============================================================
# 5. scikit-learn
# ============================================================

section(5, "scikit-learn")

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer()

    matrix = vectorizer.fit_transform(
        [
            "natural language processing",
            "machine learning",
            "language model",
        ]
    )

    print("version:", sklearn.__version__)
    print("TF-IDF shape:", matrix.shape)

    passed(
        "scikit-learn",
        f"scikit-learn {sklearn.__version__}",
    )

except Exception as exc:
    failed("scikit-learn", exc)


# ============================================================
# 6. HanLP
# ============================================================

section(6, "HanLP")

try:
    import hanlp

    print("version:", hanlp.__version__)

    # 这里只测试 HanLP runtime。
    # 不加载预训练模型，因此不会触发大型模型下载。
    passed("HanLP/import", f"HanLP {hanlp.__version__}")

except Exception as exc:
    failed("HanLP/import", exc)


# ============================================================
# Summary
# ============================================================

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

pass_count = 0
skip_count = 0
fail_count = 0

for name, status, message in RESULTS:
    if status == "PASS":
        symbol = "✓"
        pass_count += 1
    elif status == "SKIP":
        symbol = "○"
        skip_count += 1
    else:
        symbol = "✗"
        fail_count += 1

    print(f"{symbol} {status:<4} {name:<24} {message}")

print("-" * 60)
print(
    f"PASS: {pass_count} | "
    f"SKIP: {skip_count} | "
    f"FAIL: {fail_count}"
)

if fail_count:
    print("\nEnvironment contains failed tests.")
    sys.exit(1)

if skip_count:
    print("\nBasic environment is healthy; some optional datasets are missing.")
else:
    print("\nAll NLP environment tests passed.")

sys.exit(0)