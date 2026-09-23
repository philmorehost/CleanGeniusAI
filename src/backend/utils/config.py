import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).resolve().parents[3] / "config" / "config.yaml"
        self.config_path = Path(config_path)
        self.data = self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def get(self, key_path, default=None):
        keys = key_path.split(".")
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                # Check environment variable fallback
                env_key = key_path.replace(".", "_").upper()
                return os.getenv(env_key, default)
        return val
