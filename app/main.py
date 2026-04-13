import sys
from PyQt6.QtWidgets import QApplication
from app.gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("choseek1")
    app.setOrganizationName("hanenashi")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
