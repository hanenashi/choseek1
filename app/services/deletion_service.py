from pathlib import Path
from app.models.photo_pair import PhotoPair


def build_delete_plan(pairs: list[PhotoPair]) -> tuple[list[Path], list[Path]]:
    files_to_delete: list[Path] = []
    raws_to_keep: list[Path] = []

    for pair in pairs:
        if pair.keep:
            if pair.jpeg_path is not None:
                files_to_delete.append(pair.jpeg_path)
            if pair.raw_path is not None:
                raws_to_keep.append(pair.raw_path)
        else:
            if pair.jpeg_path is not None:
                files_to_delete.append(pair.jpeg_path)
            if pair.raw_path is not None:
                files_to_delete.append(pair.raw_path)

    return files_to_delete, raws_to_keep


def execute_delete_plan(files_to_delete: list[Path]) -> tuple[list[Path], list[tuple[Path, str]]]:
    deleted: list[Path] = []
    failed: list[tuple[Path, str]] = []

    for path in files_to_delete:
        try:
            if path.exists():
                path.unlink()
                deleted.append(path)
        except Exception as exc:
            failed.append((path, str(exc)))

    return deleted, failed
