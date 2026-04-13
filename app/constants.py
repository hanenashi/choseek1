from pathlib import Path

APP_NAME = "choseek1"
APP_ORG = "hanenashi"
APP_VERSION = "1.0"

SUPPORTED_JPEG_EXTS = {".jpg", ".jpeg"}
SUPPORTED_RAW_EXTS = {
    ".pef",
    ".dng",
    ".nef",
    ".cr2",
    ".cr3",
    ".arw",
    ".orf",
    ".rw2",
    ".raf",
}

DATA_DIR = Path("data")
SETTINGS_FILE = DATA_DIR / "settings.json"