# -*- coding: utf-8 -*-
"""
FocusToolbar 3.5 - Phiên bản Mèo Chào thay thế Toggle Button.
- Nút điều khiển giờ là một ảnh GIF có thể nhấp vào.
- Đã dọn dẹp và sửa lỗi cú pháp trong file gốc.
"""
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QComboBox,
    QInputDialog,
    QMessageBox,
    QFrame,
)

# === THAY ĐỔI 1: Import thêm các lớp cần thiết cho ảnh động ===
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QCoreApplication,
    Signal,
    QSize,
)
from PySide6.QtGui import QAction, QFont, QMouseEvent, QMovie
import qdarktheme
import os

# --- Cấu hình (không đổi) ---
WORK_MINUTES, SHORT_BREAK_MINUTES, LONG_BREAK_MINUTES = 25, 5, 20
ANIMATION_DURATION = 800
BUTTON_SIZE = 60
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
GIF_PATH = os.path.join(WORKING_DIR, "waving_cat.gif")
# --- Stylesheet tùy chỉnh (đã sửa lỗi cú pháp) ---
CUSTOM_STYLESHEET = """
/* Quy tắc này sẽ ghi đè lên qdarktheme để làm nền trong suốt */
#MainContainer {
    background-color: transparent;
}
/* Quy tắc này đảm bảo nút/label điều khiển luôn tròn và có màu cam */
#ToggleButton {
    background-color: #e67e22;
    border-radius: 20px;
    border: 1px solid #d35400; /* Thêm viền nhẹ cho đẹp hơn */
}
#ToggleButton:hover {
    background-color: #f39c12;
}
/* Quy tắc này đảm bảo hộp nội dung có màu nền và bo góc như thiết kế */
#CollapsibleContainer {
    /*background-color: #34495e;*/ /* Màu nền của hộp nội dung */
    border-radius: 15px;
}
"""


class ClickableLabel(QLabel):
    """
    Một lớp con của QLabel được tạo ra để có thể nhấp chuột.
    Nó phát ra một tín hiệu 'clicked' mỗi khi được nhấn.
    """

    clicked = Signal()  # Định nghĩa một tín hiệu mới tên là 'clicked'

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QMouseEvent):
        """Hàm này được tự động gọi khi người dùng nhấp chuột vào label."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # Phát ra tín hiệu 'clicked'
        super().mousePressEvent(event)


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
        self.time_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        layout.addWidget(self.time_label)

        self.start_button = QPushButton("▶")
        self.pause_button = QPushButton("❚❚")
        self.reset_button = QPushButton("↺")
        self.start_button.setFont(QFont("Segoe UI Symbol", 16))
        self.pause_button.setFont(QFont("Segoe UI Symbol", 16))
        self.reset_button.setFont(QFont("Segoe UI Symbol", 14))
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
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.task_combo = QComboBox()
        self.task_combo.setMinimumWidth(120)
        layout.addWidget(self.task_combo)
        self.add_button = QPushButton("+")
        self.add_button.setFont(QFont("Segoe UI Symbol", 16))
        self.add_button.setFixedSize(28, 28)
        layout.addWidget(self.add_button)
        self.delete_button = QPushButton("−")
        self.delete_button.setFont(QFont("Segoe UI Symbol", 16))
        self.delete_button.setFixedSize(28, 28)
        layout.addWidget(self.delete_button)
        self.add_button.clicked.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)

    def add_task(self):
        dialog = QInputDialog(self)
        dialog.setStyleSheet("QLineEdit { color: black; }")
        text, ok = dialog.getText(self, "Thêm Nhiệm vụ mới", "Tên nhiệm vụ:")
        if ok and text:
            self.task_combo.addItem(text)
            self.task_combo.setCurrentText(text)

    def delete_task(self):
        if self.task_combo.currentIndex() == -1:
            return
        reply = QMessageBox.question(
            self, "Xác nhận", f"Xóa nhiệm vụ '{self.task_combo.currentText()}'?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.task_combo.removeItem(self.task_combo.currentIndex())


class FocusToolbar(QWidget):
    """Cửa sổ nổi chính, có thể thu gọn/mở rộng."""

    def __init__(self):
        super().__init__()
        self.is_expanded, self.drag_position = False, None
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("FocusToolbar")
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        window_layout = QHBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.main_container)

        # === THAY ĐỔI 2: Thay thế QPushButton bằng ClickableLabel ===
        # Thay vì nút bấm, chúng ta tạo một label có thể nhấp chuột
        self.toggle_label = ClickableLabel(self)
        self.toggle_label.setObjectName(
            "ToggleButton"
        )  # Giữ lại tên để áp dụng style cũ
        self.toggle_label.setFixedSize(BUTTON_SIZE + 40, BUTTON_SIZE)
        self.toggle_label.clicked.connect(self.toggle_animation)

        # Tạo QMovie để hiển thị GIF

        self.movie = QMovie(GIF_PATH)  # Đảm bảo file này tồn tại
        if not self.movie.isValid():
            print("Lỗi: Không thể tải file waving_cat.gif")
            self.toggle_label.setText("🎯")  # Fallback về text nếu không có GIF
        else:
            self.toggle_label.setMovie(self.movie)
            self.movie.setScaledSize(
                QSize(BUTTON_SIZE + 40, BUTTON_SIZE)
            )  # Co giãn GIF vừa với label
            self.movie.start()  # Bắt đầu chạy ảnh động

        # ... các phần còn lại của __init__ không đổi ...
        self.collapsible_container = QWidget()
        self.collapsible_container.setObjectName("CollapsibleContainer")
        container_layout = QHBoxLayout(self.collapsible_container)
        container_layout.setContentsMargins(5, 0, 5, 0)
        container_layout.setSpacing(5)
        self.task_widget = TaskWidgetCompact()
        container_layout.addWidget(self.task_widget)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        container_layout.addWidget(line)
        self.pomodoro_widget = PomodoroWidgetCompact()
        container_layout.addWidget(self.pomodoro_widget)
        self.expanded_width = self.collapsible_container.sizeHint().width() + 10
        self.collapsible_container.setMaximumWidth(0)

        # === THAY ĐỔI 3: Thêm label vào layout thay vì nút bấm ===
        self.main_layout.addWidget(self.toggle_label)
        self.main_layout.addWidget(self.collapsible_container)
        self.main_layout.addStretch(1)

    def toggle_animation(self):
        # Hàm này không có thay đổi, nó vẫn hoạt động như cũ
        content_end_width = self.expanded_width if not self.is_expanded else 0
        window_end_width = BUTTON_SIZE + 40 + content_end_width
        self.anim_content = QPropertyAnimation(
            self.collapsible_container, b"maximumWidth"
        )
        self.anim_content.setDuration(ANIMATION_DURATION)
        self.anim_content.setEndValue(content_end_width)
        self.anim_content.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_window = QPropertyAnimation(self.main_container, b"minimumWidth")
        self.anim_window.setDuration(ANIMATION_DURATION)
        self.anim_window.setEndValue(window_end_width)
        self.anim_window.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_content.start()
        self.anim_window.start()
        self.is_expanded = not self.is_expanded

    # --- Các hàm xử lý kéo-thả và menu (đã dọn dẹp) ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = QAction("Thoát", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_stylesheet = qdarktheme.load_stylesheet("light")
    combined_stylesheet = base_stylesheet + CUSTOM_STYLESHEET
    app.setStyleSheet(combined_stylesheet)
    toolbar = FocusToolbar()
    toolbar.show()
    sys.exit(app.exec())
