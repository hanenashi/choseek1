from dataclasses import dataclass
from pathlib import Path


@dataclass
class PhotoPair:
    base_name: str
    jpeg_path: Path | None = None
    raw_path: Path | None = None
    keep: bool = False

    @property
    def has_jpeg(self) -> bool:
        return self.jpeg_path is not None

    @property
    def has_raw(self) -> bool:
        return self.raw_path is not None
