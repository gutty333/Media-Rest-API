import json
from pathlib import Path
from typing import Dict

APP_SETTINGS = "settings.json"


def check_settings() -> None:
    file = Path(APP_SETTINGS).absolute()

    if not file.exists():
        raise Exception(f"The file {APP_SETTINGS} is not found")


def get_settings_map() -> Dict[str, str]:
    check_settings()
    with open(APP_SETTINGS) as file:
        return json.load(file)