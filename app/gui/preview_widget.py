from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PreviewWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.label = QLabel("Preview area")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(300)
        self.label.setStyleSheet("border: 1px solid #555;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def set_placeholder(self, text: str) -> None:
        self.label.setText(text)
        self.label.setPixmap(QPixmap())

    def set_pixmap(self, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            self.set_placeholder("Cannot load image")
            return

        scaled = pixmap.scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.label.setPixmap(scaled)
        self.label.setText("")

    def resizeEvent(self, event) -> None:
        if self.label.pixmap() is not None:
            pixmap = self.label.pixmap()
            if pixmap is not None and not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.label.setPixmap(scaled)
        super().resizeEvent(event)
