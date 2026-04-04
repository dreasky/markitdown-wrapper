# markitdown-wrapper

基于 [MarkItDown](https://github.com/microsoft/markitdown) 的封装库，支持文档转 Markdown，并通过 VL 模型将图片替换为语义描述。

## 安装

```bash
# 作为 git submodule
git submodule add https://github.com/dreasky/markitdown-wrapper.git libs/markitdown-wrapper
pip install -e libs/markitdown-wrapper

# 可选：启用 OCR 支持
pip install -e "libs/markitdown-wrapper[ocr]"
```

## 配置

在项目根目录创建 `.env`（参考 `.env.example`）：

```
DASHSCOPE_API_KEY=your_api_key
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-vl-plus
```

### 配置文件（可选）

包内置了默认的 `markitdown_config.json`，控制 LLM 提示词和插件开关。如需覆盖，在项目根目录放同名文件，或实例化时传入路径：

```python
from markitdown_wrapper import MarkitdownWrapper
from pathlib import Path

# 使用包内置默认配置
wrapper = MarkitdownWrapper()

# 使用自定义配置
wrapper = MarkitdownWrapper(config_file=Path("my_config.json"))
```

配置项说明：

| 字段 | 默认值 | 说明 |
|---|---|---|
| `llm_prompt` | 见内置配置 | VL 模型处理图片时的提示词 |
| `enable_plugins` | `true` | 是否启用 MarkItDown 插件 |

## 使用

```python
from markitdown_wrapper import MarkitdownWrapper
from pathlib import Path

wrapper = MarkitdownWrapper()

# 文档转 Markdown（支持 docx、xlsx、pptx、pdf、图片等）
output_md = wrapper.convert(Path("report.docx"), output_dir=Path("output"))

# Markdown 中的图片替换为语义描述
wrapper.semantic_md(Path("output/report.md"), Path("output/report_semantic.md"))

# 批量处理
succeeded, failed = wrapper.semantic_md_list(
    input_files=list(Path("output").glob("*.md")),
    output_dir=Path("output/semantic"),
)
```

## 支持的输入格式

MarkItDown 支持的所有格式，包括：PDF、Word（docx）、Excel（xlsx）、PowerPoint（pptx）、图片（jpg/png 等）、HTML、CSV 等。
