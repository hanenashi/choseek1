from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.gui.preview_widget import PreviewWidget
from app.gui.status_bar import StatusBarWidget
from app.gui.thumbnail_list import ThumbnailList
from app.models.photo_pair import PhotoPair
from app.services.deletion_service import build_delete_plan, execute_delete_plan
from app.services.scanner import scan_folder
from app.services.settings_service import load_settings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("choseek1")
        self.resize(1400, 900)

        self.settings = load_settings()
        self.current_folder: Path | None = None
        self.pairs: list[PhotoPair] = []

        self.preview = PreviewWidget()
        self.thumbnails = ThumbnailList()
        self.status_widget = StatusBarWidget()

        self._build_ui()
        self._build_actions()
        self._build_shortcuts()
        self._connect_signals()

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.preview)
        splitter.addWidget(self.thumbnails)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)
        layout.addWidget(self.status_widget)

        self.setCentralWidget(central)

    def _build_actions(self) -> None:
        open_action = QAction("Open Folder", self)
        open_action.triggered.connect(self.open_folder)

        delete_action = QAction("Execute Delete", self)
        delete_action.triggered.connect(self.execute_delete)

        toggle_action = QAction("Toggle Keep/Delete", self)
        toggle_action.triggered.connect(self.toggle_current_keep)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(delete_action)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(toggle_action)

    def _build_shortcuts(self) -> None:
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, activated=self.toggle_current_keep)
        QShortcut(QKeySequence(Qt.Key.Key_K), self, activated=self.mark_current_keep)
        QShortcut(QKeySequence(Qt.Key.Key_D), self, activated=self.mark_current_delete)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, activated=self.execute_delete)

    def _connect_signals(self) -> None:
        self.thumbnails.currentItemChanged.connect(self.on_selection_changed)
        self.thumbnails.itemDoubleClicked.connect(lambda _: self.toggle_current_keep())

    def open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if not folder:
            return

        self.current_folder = Path(folder)
        self.pairs = scan_folder(self.current_folder)

        default_keep = self.settings.get("default_keep", False)
        for pair in self.pairs:
            pair.keep = default_keep

        self.thumbnails.load_pairs(self.pairs)

        if self.pairs:
            self.thumbnails.setCurrentRow(0)
            self.status_widget.set_message(f"Loaded {len(self.pairs)} JPEG entries")
        else:
            self.preview.set_placeholder("No JPEG files found")
            self.status_widget.set_message("No JPEG files found")

    def on_selection_changed(self, current, previous) -> None:
        if current is None:
            self.preview.set_placeholder("No image selected")
            return

        pair = current.data(Qt.ItemDataRole.UserRole)
        if pair and pair.jpeg_path is not None:
            pixmap = QPixmap(str(pair.jpeg_path))
            self.preview.set_pixmap(pixmap)

    def toggle_current_keep(self) -> None:
        self.thumbnails.toggle_current_keep()
        self._refresh_status()

    def mark_current_keep(self) -> None:
        item = self.thumbnails.currentItem()
        if item is None:
            return
        pair = item.data(Qt.ItemDataRole.UserRole)
        pair.keep = True
        self.thumbnails._apply_visual_state(item, pair)
        self._refresh_status()

    def mark_current_delete(self) -> None:
        item = self.thumbnails.currentItem()
        if item is None:
            return
        pair = item.data(Qt.ItemDataRole.UserRole)
        pair.keep = False
        self.thumbnails._apply_visual_state(item, pair)
        self._refresh_status()

    def _refresh_status(self) -> None:
        keep_count = sum(1 for p in self.pairs if p.keep)
        delete_count = len(self.pairs) - keep_count
        self.status_widget.set_message(
            f"Keep: {keep_count} | Delete groups: {delete_count} | Total: {len(self.pairs)}"
        )

    def execute_delete(self) -> None:
        if not self.pairs:
            QMessageBox.information(self, "Nothing to delete", "No loaded photo pairs.")
            return

        files_to_delete, raws_to_keep = build_delete_plan(self.pairs)

        msg = (
            f"Delete {len(files_to_delete)} files?\n"
            f"RAW files kept: {len(raws_to_keep)}"
        )

        reply = QMessageBox.question(
            self,
            "Confirm delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted, failed = execute_delete_plan(files_to_delete)

        QMessageBox.information(
            self,
            "Delete result",
            f"Deleted: {len(deleted)}\nFailed: {len(failed)}",
        )

        if self.current_folder is not None:
            self.pairs = scan_folder(self.current_folder)
            self.thumbnails.load_pairs(self.pairs)
            if self.pairs:
                self.thumbnails.setCurrentRow(0)
            else:
                self.preview.set_placeholder("No JPEG files found")
            self._refresh_status()
