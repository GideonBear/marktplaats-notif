from pathlib import Path
from shutil import copy

config_dir = Path("/config")
config_file = config_dir / "config.toml"

if not config_file.exists():
    copy("default_config.toml", config_file)
    print("Default configuration created")
