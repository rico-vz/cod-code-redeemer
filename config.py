import yaml
from pathlib import Path

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    
    # Default configuration
    default_config = {
        "options": {
            "min_delay_ms": 750,
            "max_delay_ms": 1450,
            "redeem_limit_max": 160,
            "window_size": {
                "width": 1280,
                "height": 720
            }
        }
    }
    
    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f)
            if user_config and isinstance(user_config, dict):
                default_config.update(user_config)
    
    return default_config
