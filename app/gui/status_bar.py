from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar, QSlider


class StatusBarWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.label = QLabel("Ready")
        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.progress_bar.setMinimumWidth(220)
        
        self.thumb_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumb_slider.setRange(80, 320)
        self.thumb_slider.setFixedWidth(150)
        self.thumb_slider.setToolTip("Thumbnail Size")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.thumb_slider)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

    def set_message(self, text: str) -> None:
        self.label.setText(text)

    def show_progress(self, text: str, minimum: int, maximum: int) -> None:
        self.progress_label.setText(text)
        self.progress_label.setVisible(True)
        self.progress_bar.setRange(minimum, maximum)
        self.progress_bar.setValue(minimum)
        self.progress_bar.setVisible(True)
        self.thumb_slider.setVisible(False)

    def update_progress_text(self, text: str) -> None:
        self.progress_label.setText(text)
        self.progress_label.setVisible(True)

    def update_progress_value(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def hide_progress(self) -> None:
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.thumb_slider.setVisible(True)