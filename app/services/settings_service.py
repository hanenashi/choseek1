import json
from app.constants import DATA_DIR, SETTINGS_FILE

DEFAULT_SETTINGS = {
    "default_keep": False,
    "zoom_levels": "50, 100, 200, 300, 500",
    "thumb_size": 160,
    "confirm_before_delete": True,
    "default_folder": "",
    "dev_safe_mode": False,
    "shortcut_toggle": "Space",
    "shortcut_keep": "K",
    "shortcut_delete": "D",
    "shortcut_execute": "Delete",
    "enable_loupe": True,
}

def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_settings() -> dict:
    ensure_data_dir()
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict) -> None:
    ensure_data_dir()
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)