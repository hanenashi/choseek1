from pathlib import Path
from app.constants import SUPPORTED_JPEG_EXTS, SUPPORTED_RAW_EXTS
from app.models.photo_pair import PhotoPair


def scan_folder(folder: Path) -> list[PhotoPair]:
    pairs: dict[str, PhotoPair] = {}

    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue

        ext = path.suffix.lower()
        stem = path.stem

        if ext not in SUPPORTED_JPEG_EXTS and ext not in SUPPORTED_RAW_EXTS:
            continue

        pair = pairs.get(stem)
        if pair is None:
            pair = PhotoPair(base_name=stem)
            pairs[stem] = pair

        if ext in SUPPORTED_JPEG_EXTS:
            pair.jpeg_path = path
        elif ext in SUPPORTED_RAW_EXTS:
            pair.raw_path = path

    return [p for p in pairs.values() if p.jpeg_path is not None]
