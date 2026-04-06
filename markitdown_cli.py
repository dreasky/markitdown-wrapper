#!/usr/bin/env python3
"""
MarkItDown CLI

Subcommands:
  convert        Convert a document/image to Markdown
  semantic       Replace images in a Markdown file with semantic descriptions
  semantic-list  Batch replace images in all Markdown files in a directory
"""

import argparse
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from markitdown_wrapper import MarkitdownWrapper


def cmd_convert(args):
    MarkitdownWrapper().convert(Path(args.input), Path(args.output))


def cmd_semantic(args):
    MarkitdownWrapper().semantic_md(Path(args.input), Path(args.output))


def cmd_semantic_list(args):
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    files = sorted(input_dir.glob("*.md"))
    if not files:
        print(f"目录中没有 .md 文件: {input_dir}", file=sys.stderr)
        return
    MarkitdownWrapper().semantic_md_list(files, output_dir)


def main():
    parser = argparse.ArgumentParser(prog="markitdown_cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="Convert a document or image to Markdown")
    p_conv.add_argument("-i", "--input", required=True, dest="input", help="Input file path")
    p_conv.add_argument("-o", "--output", required=True, dest="output", help="Output .md file path")

    p_sem = sub.add_parser("semantic", help="Replace images in a Markdown file with semantic descriptions")
    p_sem.add_argument("-i", "--input", required=True, dest="input", help="Input .md file path")
    p_sem.add_argument("-o", "--output", required=True, dest="output", help="Output .md file path")

    p_seml = sub.add_parser("semantic-list", help="Batch replace images in all .md files in a directory")
    p_seml.add_argument("-i", "--input", required=True, dest="input", help="Input directory containing .md files")
    p_seml.add_argument("-o", "--output", required=True, dest="output", help="Output directory")

    args = parser.parse_args()

    cmd_map = {
        "convert": cmd_convert,
        "semantic": cmd_semantic,
        "semantic-list": cmd_semantic_list,
    }

    try:
        cmd_map[args.command](args)
        return 0
    except FileNotFoundError as e:
        print(f"文件不存在: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"执行失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
