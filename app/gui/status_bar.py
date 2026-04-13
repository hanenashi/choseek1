from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout


class StatusBarWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.label = QLabel("Ready")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.label)

    def set_message(self, text: str) -> None:
        self.label.setText(text)
