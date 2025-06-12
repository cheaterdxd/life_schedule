# -*- coding: utf-8 -*-
"""
FocusToolbar 5.0 - Phiên bản Chu trình 3 Trạng thái (Thu gọn -> Mèo -> Công cụ).
(Dựa trên source code 4.0)
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QComboBox, QInputDialog, QMessageBox, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QCoreApplication, QSize
from PySide6.QtGui import QAction, QFont, QMouseEvent, QMovie

# --- Cấu hình ---
WORK_MINUTES, SHORT_BREAK_MINUTES, LONG_BREAK_MINUTES = 25, 5, 20
ANIMATION_DURATION = 400
BUTTON_SIZE = 40
CAT_GIF_SIZE = 64

# --- Bảng kiểu dáng ---
FOCUS_STYLESHEET = """
#FocusToolbar { background-color: transparent; }
#MainContainer { background-color: transparent; }
QWidget { color: #ecf0f1; }
#CollapsibleContainer { background-color: #34495e; border-radius: 15px; }
#ToggleButton { background-color: #e67e22; border-radius: 20px; }
#TimeLabel { color: #ffffff; }
QPushButton { background-color: #4a627a; border: none; padding: 5px; border-radius: 5px; }
QPushButton:hover { background-color: #5b6375; }
QPushButton#ToggleButton:hover { background-color: #f39c12; }
QComboBox { background-color: #4a627a; border: 1px solid #5b6375; border-radius: 5px; padding: 5px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #4a627a; border: 1px solid #5b6375; selection-background-color: #2980b9; }
"""

class PomodoroWidgetCompact(QWidget):
    # Lớp này không có thay đổi
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self.work_cycles = 0
        self.total_seconds = WORK_MINUTES * 60

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.time_label = QLabel(f"{WORK_MINUTES:02}:00")
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        layout.addWidget(self.time_label)

        self.start_button = QPushButton("▶")
        self.pause_button = QPushButton("❚❚")
        self.reset_button = QPushButton("↺")

        for btn in (self.start_button, self.pause_button, self.reset_button):
            btn.setFixedSize(28, 28)
            layout.addWidget(btn)

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button.clicked.connect(self.reset_timer)

    def start_timer(self):
        if not self.timer.isActive():
            if self.state == "idle":
                self.state = "work"
                self.total_seconds = WORK_MINUTES * 60
            self.timer.start(1000)

    def pause_timer(self):
        self.timer.stop()

    def reset_timer(self):
        self.timer.stop()
        self.state = "idle"
        self.work_cycles = 0
        self.total_seconds = WORK_MINUTES * 60
        self._update_label_text()

    def update_display(self):
        self.total_seconds -= 1
        self._update_label_text()
        if self.total_seconds < 0:
            self.timer.stop()
            self._next_cycle()

    def _update_label_text(self):
        mins, secs = divmod(self.total_seconds, 60)
        self.time_label.setText(f"{mins:02}:{secs:02}")

    def _next_cycle(self):
        if self.state == "work": 
            self.work_cycles += 1
            if self.work_cycles % 4 == 0: 
                self.state = "long_break"
                self.total_seconds = LONG_BREAK_MINUTES * 60
            else: 
                self.state = "short_break"
                self.total_seconds = SHORT_BREAK_MINUTES * 60
        else: 
            self.state = "work"
            self.total_seconds = WORK_MINUTES * 60
        self._update_label_text()
        self.start_timer()

class TaskWidgetCompact(QWidget):
    # Lớp này không có thay đổi
    def __init__(self, parent=None):
        super().__init__(parent); layout = QHBoxLayout(self); layout.setContentsMargins(5,5,5,5); layout.setSpacing(5); self.task_combo = QComboBox(); self.task_combo.setMinimumWidth(120); layout.addWidget(self.task_combo); self.add_button = QPushButton("+"); self.add_button.setFixedSize(28, 28); layout.addWidget(self.add_button); self.delete_button = QPushButton("−"); self.delete_button.setFixedSize(28, 28); layout.addWidget(self.delete_button); self.add_button.clicked.connect(self.add_task); self.delete_button.clicked.connect(self.delete_task)
    def add_task(self):
        dialog = QInputDialog(self); dialog.setStyleSheet("QLineEdit { color: black; }"); text, ok = dialog.getText(self, "Thêm Nhiệm vụ mới", "Tên nhiệm vụ:")
        if ok and text: self.task_combo.addItem(text); self.task_combo.setCurrentText(text)
    def delete_task(self):
        if self.task_combo.currentIndex() == -1: return; reply = QMessageBox.question(self, "Xác nhận", f"Xóa nhiệm vụ '{self.task_combo.currentText()}'?");
        if reply == QMessageBox.Yes: self.task_combo.removeItem(self.task_combo.currentIndex())

class FocusToolbar(QWidget):
    """Cửa sổ nổi chính, quản lý chu trình 3 trạng thái."""
    def __init__(self):
        super().__init__()
        # Trạng thái: 0 = Thu gọn, 1 = Mèo, 2 = Công cụ
        self.view_state = 0
        self.drag_position = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("FocusToolbar"); self.setStyleSheet(FOCUS_STYLESHEET)
        
        self.main_container = QWidget(); self.main_container.setObjectName("MainContainer")
        self.main_layout = QHBoxLayout(self.main_container); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(10)
        window_layout = QHBoxLayout(self); window_layout.setContentsMargins(0,0,0,0); window_layout.addWidget(self.main_container)

        # 1. Nút điều khiển (luôn hiển thị)
        self.toggle_button = QPushButton("🎯"); self.toggle_button.setObjectName("ToggleButton"); self.toggle_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self.toggle_button.clicked.connect(self.cycle_view)

        # === TẠO CÁC "TRANG" CHO QSTACKEDWIDGET ===
        # Trang 0: Mèo Chào
        self.cat_widget = QLabel()
        self.movie = QMovie("waving_cat.gif")
        if self.movie.isValid():
            self.cat_widget.setMovie(self.movie)
            self.movie.setScaledSize(QSize(CAT_GIF_SIZE, CAT_GIF_SIZE))
            self.movie.start()
        else:
            self.cat_widget.setText("Lỗi GIF!")
        # Tính toán trước chiều rộng của trang mèo
        self.cat_width = CAT_GIF_SIZE + 20 

        # Trang 1: Thanh công cụ đầy đủ
        self.focus_widget = QWidget()
        focus_layout = QHBoxLayout(self.focus_widget)
        task_widget = TaskWidgetCompact(); focus_layout.addWidget(task_widget)
        line = QFrame(); line.setFrameShape(QFrame.VLine); line.setFrameShadow(QFrame.Plain); focus_layout.addWidget(line)
        pomodoro_widget = PomodoroWidgetCompact(); focus_layout.addWidget(pomodoro_widget)
        # Tính toán trước chiều rộng của trang công cụ
        self.focus_width = self.focus_widget.sizeHint().width() + 20

        # === TẠO CÁC CONTAINER CHÍNH ===
        # 2. QStackedWidget để chứa 2 trang trên
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.cat_widget)
        self.stacked_widget.addWidget(self.focus_widget)
        
        # 3. "Hộp" có thể thu gọn, chứa QStackedWidget
        self.collapsible_container = QWidget(); self.collapsible_container.setObjectName("CollapsibleContainer")
        container_layout = QHBoxLayout(self.collapsible_container)
        container_layout.setContentsMargins(10,0,10,0)
        container_layout.addWidget(self.stacked_widget)
        self.collapsible_container.setMaximumWidth(0) # Ẩn ban đầu

        # Thêm các thành phần vào layout chính
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.collapsible_container)
        self.main_layout.addStretch(1)

    def cycle_view(self):
        """Hàm chính xử lý logic chuyển đổi giữa 3 trạng thái."""
        if self.view_state == 0: # --- Từ Thu gọn -> Mèo ---
            self.stacked_widget.setCurrentIndex(0) # Hiển thị trang Mèo
            self.animate_container(self.cat_width)
            self.view_state = 1
        elif self.view_state == 1: # --- Từ Mèo -> Công cụ ---
            self.stacked_widget.setCurrentIndex(1) # Hiển thị trang Công cụ
            self.animate_container(self.focus_width)
            self.view_state = 2
        else: # --- Từ Công cụ -> Thu gọn ---
            self.animate_container(0)
            self.view_state = 0

    def animate_container(self, target_width):
        """Hàm trợ giúp để chạy animation."""
        window_target_width = BUTTON_SIZE + target_width
        self.anim_content = QPropertyAnimation(self.collapsible_container, b"maximumWidth"); self.anim_content.setDuration(ANIMATION_DURATION); self.anim_content.setEndValue(target_width); self.anim_content.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim_window = QPropertyAnimation(self.main_container, b"minimumWidth"); self.anim_window.setDuration(ANIMATION_DURATION); self.anim_window.setEndValue(window_target_width); self.anim_window.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim_content.start(); self.anim_window.start()

    # --- Các hàm xử lý kéo-thả và menu (đã sửa lỗi) ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); event.accept()
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None: self.move(event.globalPosition().toPoint() - self.drag_position); event.accept()
    def mouseReleaseEvent(self, event: QMouseEvent): self.drag_position = None; event.accept()
    def contextMenuEvent(self, event): menu = QMenu(self); quit_action = QAction("Thoát", self); quit_action.triggered.connect(QCoreApplication.instance().quit); menu.addAction(quit_action); menu.exec(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolbar = FocusToolbar()
    toolbar.show()
    sys.exit(app.exec())
