from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QImageReader

from app.constants import SUPPORTED_JPEG_EXTS, SUPPORTED_RAW_EXTS
from app.models.photo_pair import PhotoPair


class ScanWorker(QObject):
    progress_text = pyqtSignal(str)
    progress_range = pyqtSignal(int, int)
    progress_value = pyqtSignal(int)
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, folder: Path) -> None:
        super().__init__()
        self.folder = folder

    def run(self) -> None:
        try:
            all_files = [p for p in sorted(self.folder.iterdir()) if p.is_file()]
            pairs: dict[str, PhotoPair] = {}

            self.progress_text.emit("Grouping files...")
            
            for path in all_files:
                ext = path.suffix.lower()
                if ext in SUPPORTED_JPEG_EXTS or ext in SUPPORTED_RAW_EXTS:
                    stem = path.stem
                    pair = pairs.get(stem)
                    if pair is None:
                        pair = PhotoPair(base_name=stem)
                        pairs[stem] = pair

                    if ext in SUPPORTED_JPEG_EXTS:
                        pair.jpeg_path = path
                    else:
                        pair.raw_path = path

            result = [p for p in pairs.values() if p.jpeg_path is not None]

            self.progress_text.emit("Generating thumbnails...")
            self.progress_range.emit(0, max(len(result), 1))

            for i, pair in enumerate(result, start=1):
                if pair.jpeg_path is not None:
                    reader = QImageReader(str(pair.jpeg_path))
                    reader.setAutoTransform(True)
                    orig_size = reader.size()
                    if orig_size.isValid():
                        # Extract at max slider size for crisp scaling
                        orig_size.scale(320, 320, Qt.AspectRatioMode.KeepAspectRatio)
                        reader.setScaledSize(orig_size)
                    
                    pair.thumb_image = reader.read()

                self.progress_value.emit(i)

            self.finished.emit(result)

        except Exception as exc:
            self.failed.emit(str(exc))