from pathlib import Path

from PyQt6.QtCore import Qt, QThread, QTimer, QSize, QByteArray
from PyQt6.QtGui import QAction, QKeySequence, QShortcut, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QDialog,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
    QGroupBox
)

from app.constants import APP_VERSION
from app.gui.preview_widget import PreviewWidget
from app.gui.status_bar import StatusBarWidget
from app.gui.thumbnail_list import ThumbnailList
from app.models.photo_pair import PhotoPair
from app.services.deletion_service import build_delete_plan, execute_delete_plan
from app.services.settings_service import load_settings, save_settings
from app.workers.scan_worker import ScanWorker


class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings
        self.resize(450, 420)

        self.folder_input = QLineEdit(self.settings.get("default_folder", ""))
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)

        self.zoom_input = QLineEdit(self.settings.get("zoom_levels", "50, 100, 200, 300, 500"))
        self.default_keep_cb = QCheckBox("Set newly loaded photos to KEEP by default")
        self.default_keep_cb.setChecked(self.settings.get("default_keep", False))
        self.loupe_cb = QCheckBox("Enable Magnifier (Loupe) on Right-Click")
        self.loupe_cb.setChecked(self.settings.get("enable_loupe", True))
        self.safe_mode_cb = QCheckBox("Enable Dev Safe Mode (Simulate Delete)")
        self.safe_mode_cb.setChecked(self.settings.get("dev_safe_mode", False))

        sc_group = QGroupBox("Shortcuts")
        sc_layout = QFormLayout(sc_group)
        self.sc_toggle_input = QLineEdit(self.settings.get("shortcut_toggle", "Space"))
        self.sc_keep_input = QLineEdit(self.settings.get("shortcut_keep", "K"))
        self.sc_delete_input = QLineEdit(self.settings.get("shortcut_delete", "D"))
        self.sc_exec_input = QLineEdit(self.settings.get("shortcut_execute", "Delete"))
        
        sc_layout.addRow("Toggle Keep/Delete:", self.sc_toggle_input)
        sc_layout.addRow("Mark KEEP:", self.sc_keep_input)
        sc_layout.addRow("Mark DELETE:", self.sc_delete_input)
        sc_layout.addRow("Execute Deletion:", self.sc_exec_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)

        layout = QFormLayout(self)
        layout.addRow("Default Folder:", folder_layout)
        layout.addRow("Zoom Levels (%):", self.zoom_input)
        layout.addRow("", self.default_keep_cb)
        layout.addRow("", self.loupe_cb)
        layout.addRow("", self.safe_mode_cb)
        layout.addRow(sc_group)
        layout.addRow("", save_btn)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Folder", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def accept(self):
        self.settings["default_folder"] = self.folder_input.text()
        self.settings["zoom_levels"] = self.zoom_input.text()
        self.settings["default_keep"] = self.default_keep_cb.isChecked()
        self.settings["enable_loupe"] = self.loupe_cb.isChecked()
        self.settings["dev_safe_mode"] = self.safe_mode_cb.isChecked()
        self.settings["shortcut_toggle"] = self.sc_toggle_input.text()
        self.settings["shortcut_keep"] = self.sc_keep_input.text()
        self.settings["shortcut_delete"] = self.sc_delete_input.text()
        self.settings["shortcut_execute"] = self.sc_exec_input.text()
        save_settings(self.settings)
        super().accept()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"choseek1 v{APP_VERSION}")
        self.resize(1400, 900)

        self.settings = load_settings()
        self.current_folder: Path | None = None
        self.pairs: list[PhotoPair] = []

        self.preview = PreviewWidget()
        self.thumbnails = ThumbnailList()
        self.status_widget = StatusBarWidget()

        self.scan_thread: QThread | None = None
        self.scan_worker: ScanWorker | None = None
        self.scan_in_progress = False
        
        # Restore Main Window size/position if saved
        if "window_geometry" in self.settings:
            self.restoreGeometry(QByteArray.fromBase64(self.settings["window_geometry"].encode()))
        if "window_state" in self.settings:
            self.restoreState(QByteArray.fromBase64(self.settings["window_state"].encode()))

        self._build_ui()
        self._build_actions()
        self._build_shortcuts()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.preview)
        self.splitter.addWidget(self.thumbnails)
        
        self.preview.update_zoom_levels(self.settings.get("zoom_levels", "50, 100, 200, 300, 500"))
        self.preview.loupe_enabled = self.settings.get("enable_loupe", True)
        
        saved_size = self.settings.get("thumb_size", 160)
        self.status_widget.thumb_slider.setValue(saved_size)
        self.thumbnails.set_thumb_size(saved_size)
        
        # Restore Splitter placement if saved
        if "splitter_state" in self.settings:
            self.splitter.restoreState(QByteArray.fromBase64(self.settings["splitter_state"].encode()))

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.splitter)
        layout.addWidget(self.status_widget)

        self.setCentralWidget(central)

    def _build_actions(self) -> None:
        open_action = QAction("Open Folder", self)
        open_action.triggered.connect(self.open_folder)

        delete_action = QAction("Execute Delete", self)
        delete_action.triggered.connect(self.execute_delete)
        
        close_action = QAction("Exit", self)
        close_action.setShortcut(QKeySequence("Ctrl+Q"))
        close_action.triggered.connect(self.close)

        settings_action = QAction("Preferences...", self)
        settings_action.triggered.connect(self.open_settings)
        
        help_action = QAction("TL;DR Workflow", self)
        help_action.triggered.connect(self.show_help)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(delete_action)
        file_menu.addSeparator()
        file_menu.addAction(close_action)

        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(settings_action)
        
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(help_action)

    def _build_shortcuts(self) -> None:
        self.sc_toggle = QShortcut(QKeySequence(self.settings.get("shortcut_toggle", "Space")), self)
        self.sc_toggle.activated.connect(self.toggle_current_keep_and_advance)
        
        self.sc_keep = QShortcut(QKeySequence(self.settings.get("shortcut_keep", "K")), self)
        self.sc_keep.activated.connect(self.mark_current_keep_and_advance)
        
        self.sc_delete = QShortcut(QKeySequence(self.settings.get("shortcut_delete", "D")), self)
        self.sc_delete.activated.connect(self.mark_current_delete_and_advance)
        
        self.sc_exec = QShortcut(QKeySequence(self.settings.get("shortcut_execute", "Delete")), self)
        self.sc_exec.activated.connect(self.execute_delete)

    def _update_shortcuts(self) -> None:
        self.sc_toggle.setKey(QKeySequence(self.settings.get("shortcut_toggle", "Space")))
        self.sc_keep.setKey(QKeySequence(self.settings.get("shortcut_keep", "K")))
        self.sc_delete.setKey(QKeySequence(self.settings.get("shortcut_delete", "D")))
        self.sc_exec.setKey(QKeySequence(self.settings.get("shortcut_execute", "Delete")))

    def _connect_signals(self) -> None:
        self.thumbnails.currentItemChanged.connect(self.on_selection_changed)
        self.thumbnails.itemDoubleClicked.connect(lambda _: self.toggle_current_keep())
        self.thumbnails.state_changed.connect(self._on_thumbnails_state_changed)
        
        self.preview.zoom_changed.connect(self._on_zoom_changed)
        self.preview.load_requested.connect(self.load_default_or_browse)
        self.preview.toggle_requested.connect(self.toggle_current_keep)
        self.status_widget.thumb_slider.valueChanged.connect(self._on_thumb_size_changed)

    def show_help(self) -> None:
        msg = (
            "<b>TL;DR Workflow:</b><br><br>"
            "1. Shoot RAW+JPEG and put them in one folder.<br>"
            "2. Click Load to scan them (JPEGs load instantly).<br>"
            "3. Navigate with Arrow Keys.<br>"
            "4. <b>Shift-Click</b> or <b>Ctrl-Click</b> thumbnails to multi-select.<br>"
            "5. Scroll Wheel to Zoom, Left-Click Drag to Pan, Middle-Click to Fit.<br>"
            "6. Hold Right-Click for Loupe (Magnifier).<br>"
            "7. Right-Click the ribbon for batch Keep/Delete/Invert.<br>"
            f"8. Press <b>{self.settings.get('shortcut_toggle')}</b> to toggle selected items.<br>"
            f"9. Press <b>{self.settings.get('shortcut_execute')}</b> to execute deletion.<br><br>"
            "<b>What gets deleted?</b><br>"
            "- All rejected JPEGs and RAWs.<br>"
            "- All Keeper JPEGs.<br>"
            "<i>Leaving you with only your Keeper RAWs!</i><br><br>"
            "<b>Project GitHub:</b> <a href='https://github.com/hanenashi/choseek1'>https://github.com/hanenashi/choseek1</a>"
        )
        
        box = QMessageBox(self)
        box.setWindowTitle(f"choseek1 v{APP_VERSION} Workflow")
        box.setText(msg)
        
        icon = QIcon("choseek1.ico")
        icon_pixmap = icon.pixmap(QSize(64, 64))
        
        if not icon_pixmap.isNull():
            box.setIconPixmap(icon_pixmap)
            
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        box.exec()

    def open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            self.preview.update_zoom_levels(self.settings.get("zoom_levels", "50, 100, 200, 300, 500"))
            self.preview.loupe_enabled = self.settings.get("enable_loupe", True)
            self._update_shortcuts()
            
    def _on_zoom_changed(self, pct: int) -> None:
        self.status_widget.set_message(f"Magnifier zoom set to {pct}%")
        QTimer.singleShot(2000, self._refresh_status)
        
    def _on_thumb_size_changed(self, value: int) -> None:
        self.thumbnails.set_thumb_size(value)
        self.settings["thumb_size"] = value
        # Removed the direct save_settings() here to prevent disk-spam while dragging!

    def load_default_or_browse(self) -> None:
        folder_str = self.settings.get("default_folder", "")
        if folder_str:
            path = Path(folder_str)
            if path.exists() and path.is_dir():
                self.current_folder = path
                self._start_scan(self.current_folder, "Starting folder scan...", "Loading...")
                return
        self.open_folder()

    def open_folder(self) -> None:
        if self.scan_in_progress:
            QMessageBox.information(self, "Busy", "A folder scan is already running.")
            return

        start_dir = self.settings.get("default_folder", "")
        folder = QFileDialog.getExistingDirectory(self, "Select folder", start_dir)
        if not folder:
            return

        self.current_folder = Path(folder)
        self._start_scan(self.current_folder, "Starting folder scan...", "Loading...")

    def _start_scan(self, folder: Path, status_text: str, preview_text: str) -> None:
        self.pairs = []
        self.thumbnails.clear()
        self.preview.set_placeholder(preview_text)
        self.status_widget.set_message(status_text)

        self.scan_thread = QThread(self)
        self.scan_worker = ScanWorker(folder)
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_in_progress = True

        self.scan_thread.started.connect(self.scan_worker.run)

        self.scan_worker.progress_text.connect(self._on_scan_progress_text)
        self.scan_worker.progress_range.connect(self._on_scan_progress_range)
        self.scan_worker.progress_value.connect(self._on_scan_progress_value)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.failed.connect(self._on_scan_failed)

        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.failed.connect(self.scan_thread.quit)

        self.scan_thread.finished.connect(self._cleanup_scan_thread)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_worker.finished.connect(self.scan_worker.deleteLater)
        self.scan_worker.failed.connect(self.scan_worker.deleteLater)

        self.scan_thread.start()

    def _cleanup_scan_thread(self) -> None:
        self.scan_in_progress = False
        self.scan_worker = None
        self.scan_thread = None

    def _on_scan_progress_text(self, text: str) -> None:
        self.status_widget.update_progress_text(text)

    def _on_scan_progress_range(self, minimum: int, maximum: int) -> None:
        current_text = self.status_widget.progress_label.text() or "Working..."
        self.status_widget.show_progress(current_text, minimum, maximum)

    def _on_scan_progress_value(self, value: int) -> None:
        self.status_widget.update_progress_value(value)

    def _on_scan_finished(self, pairs: list[PhotoPair]) -> None:
        self.status_widget.hide_progress()
        self.pairs = pairs

        default_keep = self.settings.get("default_keep", False)
        for pair in self.pairs:
            pair.keep = default_keep

        self.thumbnails.load_pairs(self.pairs)

        if self.pairs:
            self.thumbnails.setCurrentRow(0)
            self._refresh_status()
        else:
            self.preview.set_placeholder("No JPEG files found")
            self.status_widget.set_message("No JPEG files found")

    def _on_scan_failed(self, message: str) -> None:
        self.status_widget.hide_progress()
        self.preview.set_placeholder("Failed to scan folder")
        self.status_widget.set_message("Folder scan failed")
        QMessageBox.critical(self, "Scan failed", message)

    def on_selection_changed(self, current, previous) -> None:
        if current is None:
            self.preview.set_placeholder("No image selected")
            return

        pair = current.data(Qt.ItemDataRole.UserRole)
        if pair and pair.jpeg_path is not None:
            self.preview.set_image_path(str(pair.jpeg_path))
            self.preview.set_keep_state(pair.keep)

    def toggle_current_keep(self) -> None:
        items = self.thumbnails.selectedItems()
        if not items: return
        for item in items:
            pair = item.data(Qt.ItemDataRole.UserRole)
            pair.keep = not pair.keep
            self.thumbnails._apply_visual_state(item, pair)
        self._on_thumbnails_state_changed()

    def toggle_current_keep_and_advance(self) -> None:
        self.toggle_current_keep()
        self._move_next()

    def mark_current_keep(self) -> None:
        items = self.thumbnails.selectedItems()
        if not items: return
        for item in items:
            pair = item.data(Qt.ItemDataRole.UserRole)
            pair.keep = True
            self.thumbnails._apply_visual_state(item, pair)
        self._on_thumbnails_state_changed()

    def mark_current_keep_and_advance(self) -> None:
        self.mark_current_keep()
        self._move_next()

    def mark_current_delete(self) -> None:
        items = self.thumbnails.selectedItems()
        if not items: return
        for item in items:
            pair = item.data(Qt.ItemDataRole.UserRole)
            pair.keep = False
            self.thumbnails._apply_visual_state(item, pair)
        self._on_thumbnails_state_changed()

    def mark_current_delete_and_advance(self) -> None:
        self.mark_current_delete()
        self._move_next()

    def _on_thumbnails_state_changed(self) -> None:
        item = self.thumbnails.currentItem()
        if item:
            pair = item.data(Qt.ItemDataRole.UserRole)
            self.preview.set_keep_state(pair.keep)
        self._refresh_status()

    def _move_next(self) -> None:
        row = self.thumbnails.currentRow()
        if row < self.thumbnails.count() - 1:
            self.thumbnails.setCurrentRow(row + 1)

    def _refresh_status(self) -> None:
        keep_count = sum(1 for p in self.pairs if p.keep)
        delete_count = len(self.pairs) - keep_count
        
        mode_text = "[DEV SAFE MODE] " if self.settings.get("dev_safe_mode") else ""
        
        self.status_widget.set_message(
            f"{mode_text}Keep: {keep_count} | Delete groups: {delete_count} | Total: {len(self.pairs)}"
        )

    def execute_delete(self) -> None:
        if self.scan_in_progress:
            QMessageBox.information(self, "Busy", "Please wait until folder scan finishes.")
            return

        if not self.pairs:
            QMessageBox.information(self, "Nothing to delete", "No loaded photo pairs.")
            return

        safe_mode = self.settings.get("dev_safe_mode", False)
        files_to_delete, raws_to_keep = build_delete_plan(self.pairs)
        
        jpeg_delete_count = sum(1 for p in files_to_delete if p.suffix.lower() in {".jpg", ".jpeg"})
        raw_delete_count = len(files_to_delete) - jpeg_delete_count

        msg = (
            f"{'SIMULATED ' if safe_mode else ''}JPEGs to delete: {jpeg_delete_count}\n"
            f"{'SIMULATED ' if safe_mode else ''}RAWs to delete: {raw_delete_count}\n"
            f"RAWs to keep: {len(raws_to_keep)}\n\n"
            f"Proceed?"
        )

        reply = QMessageBox.question(
            self,
            f"Confirm {'Simulated ' if safe_mode else ''}Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted, failed = execute_delete_plan(files_to_delete, safe_mode)

        QMessageBox.information(
            self,
            "Delete result",
            f"{'Simulated ' if safe_mode else 'Actual '}Deleted: {len(deleted)}\nFailed: {len(failed)}",
        )

        if self.current_folder is not None:
            self._start_scan(self.current_folder, "Refreshing folder...", "Refreshing...")

    def closeEvent(self, event) -> None:
        if self.scan_thread is not None and self.scan_thread.isRunning():
            QMessageBox.information(self, "Busy", "Please wait until the folder scan finishes.")
            event.ignore()
            return
            
        # Bulk save all UI states gracefully on exit
        self.settings["thumb_size"] = self.status_widget.thumb_slider.value()
        self.settings["splitter_state"] = self.splitter.saveState().toBase64().data().decode()
        self.settings["window_geometry"] = self.saveGeometry().toBase64().data().decode()
        self.settings["window_state"] = self.saveState().toBase64().data().decode()
        save_settings(self.settings)
        
        super().closeEvent(event)