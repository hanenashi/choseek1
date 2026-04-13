from PyQt6.QtCore import Qt, QSize, QRectF, pyqtSignal
from PyQt6.QtGui import QFontMetrics, QIcon, QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu

from app.models.photo_pair import PhotoPair


class ThumbnailList(QListWidget):
    state_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.thumb_size = 160

        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setWrapping(False)
        self.setUniformItemSizes(True)
        
        # Enable Shift-Click and Ctrl-Click multi-selection natively
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Enable custom context menu for Right-Clicks
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.setStyleSheet("""
            QListWidget { 
                border: none;
                border-top: 1px solid #444; 
                padding: 16px; 
                background: #161616;
            }
            QListWidget::item { 
                background: transparent; 
                border: 3px solid transparent; 
                border-radius: 15px; 
                padding: 2px;
            }
            QListWidget::item:selected { 
                background: transparent; 
                border: 3px solid #55aaff; 
            }
        """)

        self.setSpacing(8)
        self.setWordWrap(False)
        self.set_thumb_size(self.thumb_size)

    def set_thumb_size(self, size: int) -> None:
        self.thumb_size = size
        self.setIconSize(QSize(size, size))
        self.setGridSize(QSize(size + 16, size + 16))
        
        target_height = size + 56
        self.setMinimumHeight(target_height)
        self.setMaximumHeight(target_height + 20)
        
        for i in range(self.count()):
            item = self.item(i)
            pair = item.data(Qt.ItemDataRole.UserRole)
            self._apply_visual_state(item, pair)

    def load_pairs(self, pairs: list[PhotoPair]) -> None:
        self.clear()
        self.setIconSize(QSize(self.thumb_size, self.thumb_size))
        self.setGridSize(QSize(self.thumb_size + 16, self.thumb_size + 16))

        for pair in pairs:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, pair)
            self._apply_visual_state(item, pair)
            self.addItem(item)

    def _show_context_menu(self, pos) -> None:
        if not self.selectedItems():
            return
            
        menu = QMenu(self)
        keep_action = menu.addAction("Mark Selected as KEEP")
        delete_action = menu.addAction("Mark Selected as DELETE")
        menu.addSeparator()
        invert_action = menu.addAction("Invert Selection State")

        action = menu.exec(self.mapToGlobal(pos))
        if action == keep_action:
            self.set_selected_keep(True)
        elif action == delete_action:
            self.set_selected_keep(False)
        elif action == invert_action:
            self.invert_selected()

    def set_selected_keep(self, state: bool) -> None:
        for item in self.selectedItems():
            pair = item.data(Qt.ItemDataRole.UserRole)
            pair.keep = state
            self._apply_visual_state(item, pair)
        self.state_changed.emit()

    def invert_selected(self) -> None:
        for item in self.selectedItems():
            pair = item.data(Qt.ItemDataRole.UserRole)
            pair.keep = not pair.keep
            self._apply_visual_state(item, pair)
        self.state_changed.emit()

    def _apply_visual_state(self, item: QListWidgetItem, pair: PhotoPair) -> None:
        size = self.thumb_size
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        bg_color = QColor(45, 90, 45) if pair.keep else QColor(74, 32, 32)
        text_color = QColor(255, 255, 255) if pair.keep else QColor(170, 170, 170)
        status_text = "KEEP" if pair.keep else "DELETE"

        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, 12, 12)
        painter.setClipPath(path)
        painter.fillRect(0, 0, size, size, bg_color)

        text_h = max(24, int(size * 0.2))
        img_area_h = size - text_h
        
        if pair.thumb_image is not None and not pair.thumb_image.isNull():
            scaled_img = pair.thumb_image.scaled(
                size, img_area_h, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            x = (size - scaled_img.width()) // 2
            y = (img_area_h - scaled_img.height()) // 2
            painter.drawImage(x, y, scaled_img)

        text_rect = QRectF(0, size - text_h, size, text_h)
        font = painter.font()
        font.setPointSize(max(8, int(size * 0.05)))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(text_color)
        
        display_text = f"{pair.base_name} [{status_text}]"
        metrics = QFontMetrics(font)
        elided = metrics.elidedText(display_text, Qt.TextElideMode.ElideRight, size - 8)
        
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, elided)
        painter.end()
        
        item.setIcon(QIcon(pixmap))
        item.setText("")