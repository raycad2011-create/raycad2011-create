"""Configuration loader for Light."""
import json
import os
from pathlib import Path


def load_config():
    """Load configuration from config.json."""
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    return config


def get_config_value(key: str, default=None):
    """Get a specific config value by key (supports dot notation)."""
    config = load_config()
    keys = key.split(".")
    value = config
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
            if value is None:
                return default
        else:
            return default
    
    return value
