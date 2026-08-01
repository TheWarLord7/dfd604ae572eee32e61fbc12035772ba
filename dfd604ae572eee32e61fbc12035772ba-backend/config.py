import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file(path: Path):
    values = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


ENV_VALUES = _load_env_file(ENV_FILE)


def get_setting(name: str, default=None):
    return os.environ.get(name, ENV_VALUES.get(name, default))


OPENROUTER_API_KEY = get_setting("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = get_setting("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
OLLAMA_MODEL = get_setting("OLLAMA_MODEL", "qwen2.5:7b")
DEFAULT_LLM_ENGINE = get_setting("DEFAULT_LLM_ENGINE", "ollama")
