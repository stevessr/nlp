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

## 其他命令

统计文本字频和词频：

```bash
uv run text-frequency article.txt
```
