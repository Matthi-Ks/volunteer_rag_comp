import yaml;
from pathlib import Path

def load_config():
    current_dir = Path(__file__).parent.resolve()

    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.yml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)


    raise FileNotFoundError(f"Could not find 'config.yml' in {current_dir} or any of its parent directories.")