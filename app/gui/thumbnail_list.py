from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from app.models.photo_pair import PhotoPair


class ThumbnailList(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setSpacing(8)
        self.setWrapping(False)
        self.setUniformItemSizes(True)
        self.setIconSize(self.iconSize())

    def load_pairs(self, pairs: list[PhotoPair]) -> None:
        self.clear()

        for pair in pairs:
            item = QListWidgetItem(pair.base_name)
            item.setData(Qt.ItemDataRole.UserRole, pair)

            if pair.jpeg_path is not None:
                pixmap = QPixmap(str(pair.jpeg_path))
                if not pixmap.isNull():
                    thumb = pixmap.scaled(
                        160,
                        100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    item.setIcon(QIcon(thumb))

            self._apply_visual_state(item, pair)
            self.addItem(item)

    def toggle_current_keep(self) -> None:
        item = self.currentItem()
        if item is None:
            return

        pair = item.data(Qt.ItemDataRole.UserRole)
        pair.keep = not pair.keep
        self._apply_visual_state(item, pair)

    def _apply_visual_state(self, item: QListWidgetItem, pair: PhotoPair) -> None:
        suffix = "KEEP" if pair.keep else "DELETE"
        item.setText(f"{pair.base_name}\n[{suffix}]")
