import sys
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtWidgets import QApplication
from app.gui.main_window import MainWindow


def set_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(210, 210, 210))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(210, 210, 210))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(210, 210, 210))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("choseek1")
    app.setOrganizationName("hanenashi")
    
    # Set the icon
    app.setWindowIcon(QIcon("choseek1.ico"))
    
    set_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())