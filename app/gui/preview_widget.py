from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal, QRect
from PyQt6.QtGui import QPixmap, QImageReader, QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QPushButton


def load_exif_oriented_pixmap(image_path: str) -> QPixmap:
    reader = QImageReader(image_path)
    reader.setAutoTransform(True)
    image = reader.read()
    if not image.isNull():
        return QPixmap.fromImage(image)
    return QPixmap()


class PreviewWidget(QWidget):
    zoom_changed = pyqtSignal(int)
    load_requested = pyqtSignal()
    toggle_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(300)
        self.setStyleSheet("border: 1px solid #444;")
        
        self._original_pixmap = QPixmap()
        self._placeholder_text = ""
        
        self.keep_state: bool | None = None
        self.badge_rect = QRect()

        self.loupe_enabled = True
        self.zoom_levels = [0.5, 1.0, 2.0, 3.0, 5.0]
        self.current_zoom_idx = 1
        
        self.is_magnifying = False
        self.potential_loupe = False
        
        self.mag_pos = QPoint()
        self.mag_size = 350
        
        self.preview_scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.is_panning = False
        self.last_pan_pos = QPoint()
        self.click_start_pos = QPoint()

        self.load_btn = QPushButton("Load Folder", self)
        self.load_btn.setFixedSize(200, 60)
        font = self.load_btn.font()
        font.setPointSize(14)
        self.load_btn.setFont(font)
        self.load_btn.clicked.connect(self.load_requested.emit)

    def update_zoom_levels(self, levels_str: str) -> None:
        try:
            parts = [int(x.strip()) for x in levels_str.split(",") if x.strip().isdigit()]
            valid_levels = [max(10, min(1000, p)) / 100.0 for p in parts]
            if valid_levels:
                self.zoom_levels = valid_levels
                self.current_zoom_idx = min(self.current_zoom_idx, len(self.zoom_levels) - 1)
        except Exception:
            pass

    def set_placeholder(self, text: str) -> None:
        self._original_pixmap = QPixmap()
        self._placeholder_text = text
        self.keep_state = None
        self.load_btn.setVisible(True)
        self.preview_scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    def set_image_path(self, image_path: str) -> None:
        pixmap = load_exif_oriented_pixmap(image_path)
        self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            self.set_placeholder("Cannot load image")
            return

        self._original_pixmap = pixmap
        self.load_btn.setVisible(False)
        self.preview_scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()
        
    def set_keep_state(self, state: bool | None) -> None:
        self.keep_state = state
        self.update()

    def resizeEvent(self, event) -> None:
        self.load_btn.move((self.width() - self.load_btn.width()) // 2, (self.height() - self.load_btn.height()) // 2)
        super().resizeEvent(event)

    def wheelEvent(self, event) -> None:
        if self._original_pixmap.isNull(): return
        
        delta = event.angleDelta().y()
        if delta == 0: return

        old_scale = self.preview_scale
        zoom_factor = 1.15 if delta > 0 else 1.0 / 1.15
        self.preview_scale *= zoom_factor
        self.preview_scale = max(1.0, min(self.preview_scale, 20.0))

        if self.preview_scale == 1.0:
            self.pan_x = 0.0
            self.pan_y = 0.0
        else:
            win_w, win_h = self.width(), self.height()
            orig_w, orig_h = self._original_pixmap.width(), self._original_pixmap.height()
            base_scale = min(win_w / orig_w, win_h / orig_h)

            draw_w_old = orig_w * base_scale * old_scale
            x_offset_old = (win_w - draw_w_old) / 2 + self.pan_x
            draw_w_new = orig_w * base_scale * self.preview_scale
            
            mouse_x = event.position().x()
            image_u = (mouse_x - x_offset_old) / draw_w_old
            x_offset_new = mouse_x - image_u * draw_w_new
            self.pan_x = x_offset_new - (win_w - draw_w_new) / 2

            draw_h_old = orig_h * base_scale * old_scale
            y_offset_old = (win_h - draw_h_old) / 2 + self.pan_y
            draw_h_new = orig_h * base_scale * self.preview_scale
            
            mouse_y = event.position().y()
            image_v = (mouse_y - y_offset_old) / draw_h_old
            y_offset_new = mouse_y - image_v * draw_h_new
            self.pan_y = y_offset_new - (win_h - draw_h_new) / 2

        self.update()

    def mousePressEvent(self, event) -> None:
        if self._original_pixmap.isNull(): return
        
        self.click_start_pos = event.pos()
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.keep_state is not None and self.badge_rect.contains(event.pos()):
                self.toggle_requested.emit()
                return
            
            self.is_panning = True
            self.last_pan_pos = event.pos()
            
        elif event.button() == Qt.MouseButton.RightButton:
            if self.loupe_enabled:
                self.potential_loupe = True
                
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Zoom to Fit
            self.preview_scale = 1.0
            self.pan_x = 0.0
            self.pan_y = 0.0
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self.is_panning:
            delta = event.pos() - self.last_pan_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_pan_pos = event.pos()
            self.update()
            
        elif self.potential_loupe:
            # If mouse moves far enough, trigger loupe mode and cancel "click" potential
            if (event.pos() - self.click_start_pos).manhattanLength() > 5:
                self.potential_loupe = False
                self.is_magnifying = True
                self.mag_pos = event.pos()
                self.update()
                
        elif self.is_magnifying:
            self.mag_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            
        elif event.button() == Qt.MouseButton.RightButton:
            if self.potential_loupe:
                # User never dragged, process as a click
                self.current_zoom_idx = (self.current_zoom_idx + 1) % len(self.zoom_levels)
                zoom_pct = int(self.zoom_levels[self.current_zoom_idx] * 100)
                self.zoom_changed.emit(zoom_pct)
                self.potential_loupe = False
                
            if self.is_magnifying:
                self.is_magnifying = False
                
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().color(self.backgroundRole()))

        if self._original_pixmap.isNull():
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(self.rect().adjusted(0, 100, 0, 0), Qt.AlignmentFlag.AlignCenter, self._placeholder_text)
            return

        win_w = self.width()
        win_h = self.height()
        orig_w = self._original_pixmap.width()
        orig_h = self._original_pixmap.height()

        base_scale = min(win_w / orig_w, win_h / orig_h)
        draw_w = orig_w * base_scale * self.preview_scale
        draw_h = orig_h * base_scale * self.preview_scale

        x_offset = (win_w - draw_w) / 2 + self.pan_x
        y_offset = (win_h - draw_h) / 2 + self.pan_y

        target_rect = QRectF(x_offset, y_offset, draw_w, draw_h)
        source_rect = QRectF(0, 0, orig_w, orig_h)

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(target_rect, self._original_pixmap, source_rect)

        if self.keep_state is not None:
            self._draw_overlay_badge(painter)

        if self.is_magnifying:
            self._draw_magnifier(painter, x_offset, y_offset, draw_w, draw_h)
            
    def _draw_overlay_badge(self, painter: QPainter) -> None:
        text = "KEEP" if self.keep_state else "DELETE"
        bg_color = QColor(45, 90, 45, 200) if self.keep_state else QColor(90, 32, 32, 200)
        
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        w, h = 120, 40
        x = 20
        y = 20
        self.badge_rect = QRect(x, y, w, h)
        
        painter.drawRoundedRect(self.badge_rect, 5, 5)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(self.badge_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_magnifier(self, painter: QPainter, target_x_offset: float, target_y_offset: float, draw_w: float, draw_h: float) -> None:
        zoom = self.zoom_levels[self.current_zoom_idx]
        mouse_x = self.mag_pos.x()
        mouse_y = self.mag_pos.y()

        img_x = mouse_x - target_x_offset
        img_y = mouse_y - target_y_offset

        orig_w = self._original_pixmap.width()
        orig_h = self._original_pixmap.height()

        if draw_w <= 0 or draw_h <= 0: return

        orig_x = img_x * (orig_w / draw_w)
        orig_y = img_y * (orig_h / draw_h)

        src_w = self.mag_size / zoom
        src_h = self.mag_size / zoom
        src_x = orig_x - (src_w / 2)
        src_y = orig_y - (src_h / 2)

        target_rect = QRectF(mouse_x - (self.mag_size / 2), mouse_y - (self.mag_size / 2), self.mag_size, self.mag_size)
        source_rect = QRectF(src_x, src_y, src_w, src_h)

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(target_rect, self._original_pixmap, source_rect)

        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.setPen(QPen(QColor(0, 0, 0, 200), 2))
        painter.drawRect(target_rect)
        
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(target_rect.adjusted(8, 8, -8, -8), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, f"{int(zoom*100)}%")