# nlp

这是一个使用 Python 和 uv 管理的自然语言处理练习项目。

## 安装依赖

```bash
uv sync
```

## AutoTokenizer CLI

`auto-tokenizer` 使用 Hugging Face `AutoTokenizer` 将文本转换为模型对应的 token、`input_ids` 和 `attention_mask`。首次使用某个模型时，Transformers 会从 Hugging Face 下载 tokenizer 文件并缓存到本地。

直接传入文本：

```bash
uv run auto-tokenizer "我喜欢自然语言处理。"
```

从 UTF-8 文件读取：

```bash
uv run auto-tokenizer --file article.txt
```

指定模型、限制长度并输出 JSON：

```bash
uv run auto-tokenizer \
  --model bert-base-chinese \
  --max-length 128 \
  --json \
  "我喜欢自然语言处理。"
```

默认模型是 `bert-base-chinese`，默认会加入模型需要的特殊 token（例如 `[CLS]` 和 `[SEP]`）。如果不需要特殊 token，可以使用：

```bash
uv run auto-tokenizer --no-special-tokens "我喜欢自然语言处理。"
```

查看全部参数：

```bash
uv run auto-tokenizer --help
```

## 文本清理 CLI

`text-clean` 用于清理 UTF-8 文本。默认会执行 NFKC Unicode 规范化、压缩行内连续空白并删除空行；删除 URL、数字、标点以及转换小写均为可选操作。

清理文件并输出到终端：

```bash
uv run text-clean article.txt
```

写入新文件：

```bash
uv run text-clean article.txt -o article.cleaned.txt
```

执行更强的清理：

```bash
uv run text-clean article.txt \
  --lower \
  --remove-urls \
  --remove-numbers \
  --remove-punctuation \
  -o article.cleaned.txt
```

也可以作为 Unix 管道使用；省略文件名或使用 `-` 时会从标准输入读取：

```bash
cat article.txt | uv run text-clean - --remove-urls
```

如果需要保留原始连续空白或空行：

```bash
uv run text-clean article.txt --keep-whitespace --keep-blank-lines
```

Unicode 规范化默认使用 `NFKC`，也可以选择 `NFC`、`NFD`、`NFKD` 或关闭：

```bash
uv run text-clean article.txt --normalize none
```

在 Python 中也可以直接复用：

```python
from nlp.text_clean import clean_text

cleaned = clean_text(
    text,
    lower=True,
    remove_urls=True,
    remove_punctuation=True,
)
```

查看全部参数：

```bash
uv run text-clean --help
```

## 其他命令

统计文本字频和词频：

```bash
uv run text-frequency article.txt
```
