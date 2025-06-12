import sys
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel
)

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from app.constants import WORK_MINUTES, SHORT_BREAK_MINUTES, LONG_BREAK_MINUTES

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

        # Các nút điều khiển Pomodoro
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
        
        # ### THAY ĐỔI 1: Thêm nút Focus Mode ###
        self.focus_mode_button = QPushButton("Focus: OFF")
        self.focus_mode_button.setCheckable(True) # Biến nó thành một nút bật/tắt
        self.focus_mode_button.setFixedWidth(80) # Đặt chiều rộng cố định để không bị giật khi text thay đổi
        # ### THAY ĐỔI 2: Kết nối tín hiệu 'toggled' để xử lý thay đổi giao diện ###
        self.focus_mode_button.toggled.connect(self._on_focus_mode_toggled)
        
        layout.addWidget(self.focus_mode_button) # Thêm nút vào layout

    def _on_focus_mode_toggled(self, is_checked):
        """
        Hàm này được gọi mỗi khi trạng thái của nút Focus Mode thay đổi.
        Nó CHỈ chịu trách nhiệm cập nhật text của nút.
        """
        if is_checked:
            self.focus_mode_button.setText("Focus: ON")
            print("Giao diện: Nút Focus đã được BẬT.") # In ra để kiểm tra
        else:
            self.focus_mode_button.setText("Focus: OFF")
            print("Giao diện: Nút Focus đã được TẮT.") # In ra để kiểm tra
        
        # TODO: Sau này, logic backend (chặn/gỡ chặn web) sẽ được gọi từ đây.
        
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

