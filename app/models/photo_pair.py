from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtGui import QImage


@dataclass
class PhotoPair:
    base_name: str
    jpeg_path: Path | None = None
    raw_path: Path | None = None
    keep: bool = False
    thumb_image: QImage | None = None

    @property
    def has_jpeg(self) -> bool:
        return self.jpeg_path is not None

    @property
    def has_raw(self) -> bool:
        return self.raw_path is not None