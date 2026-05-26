import os
import re
from typing import Any

import yaml
from utils.path_tool import get_abs_path

ENV_PATTERN = re.compile(r"^\$\{([A-Z0-9_]+)\}$")


def resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: resolve_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_env_placeholders(item) for item in value]
    if isinstance(value, str):
        match = ENV_PATTERN.match(value.strip())
        if match:
            return os.getenv(match.group(1), value)
    return value


def load_yaml_config(config_path: str, encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        config = yaml.load(f, Loader=yaml.FullLoader) or {}
        return resolve_env_placeholders(config)


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8"):
    return load_yaml_config(config_path, encoding)

def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    return load_yaml_config(config_path, encoding)

def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    return load_yaml_config(config_path, encoding)

def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    return load_yaml_config(config_path, encoding)

rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()
