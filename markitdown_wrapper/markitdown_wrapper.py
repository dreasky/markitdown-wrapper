"""MarkItDown Wrapper — replace images in Markdown with semantic descriptions."""

import re
import sys
from pathlib import Path

from markitdown import MarkItDown
from openai import OpenAI

from .config import ConfigLoader


_MD_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HTML_IMG = re.compile(
    r'(?:<[^>]+>\s*)*<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>(?:\s*</[^>]+>)*',
    re.IGNORECASE,
)


def _detect_encoding(file_path: Path) -> str:
    for enc in (
        "utf-8",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "gbk",
        "gb2312",
        "gb18030",
    ):
        try:
            file_path.open("r", encoding=enc).read(1024)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    try:
        import chardet

        result = chardet.detect(file_path.read_bytes()[:10000])
        if result["encoding"]:
            return result["encoding"]
    except ImportError:
        pass
    return "utf-8"


def _resolve_image_path(src: str, md_dir: Path) -> str:
    if src.startswith(("http://", "https://", "data:")):
        return src
    p = Path(src)
    return src if p.is_absolute() else str((md_dir / src).resolve())


def _display_src(src: str, max_len: int = 50) -> str:
    if src.startswith("data:"):
        mime = src[5 : src.index(";")] if ";" in src else "image"
        return f"[base64:{mime}]"
    return src if len(src) <= max_len else src[:max_len] + "..."


class MarkitdownWrapper:

    def __init__(self):
        config = ConfigLoader()
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self._md = MarkItDown(
            enable_plugins=config.enable_plugins,
            llm_client=client,
            llm_model=config.model_name,
            llm_prompt=config.llm_prompt,
        )

    def _describe(self, src: str, md_dir: Path) -> str:
        resolved = _resolve_image_path(src, md_dir)
        label = _display_src(src)
        try:
            text_content = self._md.convert(resolved).text_content
            return f"\n```markdown\n{text_content}\n```\n"
        except FileNotFoundError:
            print(f"[图片语义化失败] 文件不存在: {label}", file=sys.stderr)
            return f"[图片不存在: {label}]"
        except Exception as e:
            print(
                f"[图片语义化失败] {label} - {type(e).__name__}: {e}", file=sys.stderr
            )
            return f"[图片处理失败: {label}]"

    def convert(self, file: Path, output_dir: Path) -> Path:
        """Convert a document/image to Markdown."""
        output_dir.mkdir(parents=True, exist_ok=True)

        result = self._md.convert(str(file), keep_data_uris=True)

        output_md = output_dir / (file.stem + ".md")
        output_md.write_text(result.text_content, encoding="utf-8")
        return output_md

    def semantic_md(self, input_file: Path, output_file: Path) -> None:
        """Replace images in a Markdown file with semantic descriptions."""
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        content = input_file.read_text(encoding=_detect_encoding(input_file))
        md_dir = input_file.parent
        cache: dict[str, str] = {}

        def replace(src: str) -> str:
            if src not in cache:
                cache[src] = self._describe(src, md_dir)
            return cache[src]

        content = _MD_IMG.sub(lambda m: replace(m.group(2)), content)
        content = _HTML_IMG.sub(lambda m: replace(m.group(1)), content)

        failed = sum(1 for v in cache.values() if v.startswith("[图片"))
        print(
            f"[图片语义化] {input_file.name}: 共 {len(cache)} 张, "
            f"成功 {len(cache) - failed} 张, 失败 {failed} 张",
            file=sys.stderr,
        )

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")

    def semantic_md_list(
        self, input_files: list[Path], output_dir: Path
    ) -> tuple[list[Path], list[Path]]:
        """Batch process Markdown files. Returns (succeeded, failed)."""
        succeeded, failed = [], []
        for f in input_files:
            out = output_dir / f.name
            try:
                self.semantic_md(f, out)
                succeeded.append(out)
            except Exception as e:
                print(f"[图片语义化失败] {f.name}: {e}", file=sys.stderr)
                failed.append(f)

        print(
            f"[图片语义化] 共 {len(input_files)} 个文件: "
            f"成功 {len(succeeded)} 个, 失败 {len(failed)} 个",
            file=sys.stderr,
        )
        return succeeded, failed
