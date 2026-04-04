"""Configuration loader for MarkItDown wrapper."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class ConfigLoader:

    _DEFAULT = {"llm_prompt": "请输出图片描述信息", "enable_plugins": True}

    def __init__(self):
        skill_dir = Path(__file__).parent.parent.parent
        env_file = skill_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)

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
        config_file = skill_dir / "markitdown_config.json"
        if config_file.exists():
            for k, v in json.loads(config_file.read_text(encoding="utf-8")).items():
                cfg[k] = v["value"] if isinstance(v, dict) and "value" in v else v

        self.llm_prompt: str = cfg.get("llm_prompt", self._DEFAULT["llm_prompt"])
        self.enable_plugins: bool = cfg.get("enable_plugins", self._DEFAULT["enable_plugins"])
