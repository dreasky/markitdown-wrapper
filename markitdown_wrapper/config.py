"""Configuration loader for MarkItDown wrapper."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class ConfigLoader:

    _DEFAULT = {"llm_prompt": "请输出图片描述信息", "enable_plugins": True}

    def __init__(self, config_file: Path | None = None):
        load_dotenv()

        missing = [k for k in ("DASHSCOPE_API_KEY", "BASE_URL", "MODEL_NAME")
                   if not os.environ.get(k)]
        if missing:
            for k in missing:
                print(f"Error: {k} not configured in environment", file=sys.stderr)
            sys.exit(1)

        self.api_key = os.environ["DASHSCOPE_API_KEY"]
        self.base_url = os.environ["BASE_URL"]
        self.model_name = os.environ["MODEL_NAME"]

        cfg = self._DEFAULT.copy()
        # 优先级：传入参数 > cwd/markitdown_config.json > 包内置默认配置
        _builtin = Path(__file__).parent / "markitdown_config.json"
        for path in (_builtin, config_file or Path.cwd() / "markitdown_config.json"):
            if path and path.exists():
                for k, v in json.loads(path.read_text(encoding="utf-8")).items():
                    cfg[k] = v["value"] if isinstance(v, dict) and "value" in v else v

        self.llm_prompt: str = cfg.get("llm_prompt", self._DEFAULT["llm_prompt"])
        self.enable_plugins: bool = cfg.get("enable_plugins", self._DEFAULT["enable_plugins"])
