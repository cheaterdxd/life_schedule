# -*- coding: utf-8 -*-
"""
FocusToolbar 3.2 - Phiên bản "Một Dòng" Siêu Tinh Gọn.
- Tất cả các thành phần trong mỗi widget con được đưa lên cùng một hàng.
- (Phiên bản hoàn chỉnh, sửa lỗi bị cắt)
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QComboBox, QInputDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QCoreApplication
from PySide6.QtGui import QAction, QFont, QMouseEvent
import qdarktheme

# --- Cấu hình (không đổi) ---
WORK_MINUTES, SHORT_BREAK_MINUTES, LONG_BREAK_MINUTES = 25, 5, 20
ANIMATION_DURATION = 700
BUTTON_SIZE = 40
   
CUSTOM_STYLESHEET = """
/* Quy tắc này sẽ ghi đè lên qdarktheme để làm nền trong suốt */
#MainContainer { 
    background-color: transparent; 
}

/* Quy tắc này đảm bảo nút điều khiển luôn tròn và có màu cam */
#ToggleButton { 
    /*background-color: #e67e22;*/ 
    border-radius: 20px;
    border-width: 5px;
    border-style: solid;
}
#ToggleButton:hover { 
    background-color: #f39c12; 
}

/* Quy tắc này đảm bảo hộp nội dung có màu nền và bo góc như thiết kế */
#CollapsibleContainer { 
    /*background-color: #34495e;*/ 
    border-radius: 15px; 
}
"""

class PomodoroWidgetCompact(QWidget):
    """Widget Pomodoro phiên bản "một dòng"."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state, self.work_cycles, self.total_seconds = "idle", 0, WORK_MINUTES * 60
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_display)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5,5,5,5) # Lề xung quanh widget
        layout.setSpacing(5) # Khoảng cách giữa các thành phần

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
            if self.state == "idle": self.state = "work"; self.total_seconds = WORK_MINUTES * 60
            self.timer.start(1000)
    def pause_timer(self): self.timer.stop()
    def reset_timer(self):
        self.timer.stop(); self.state = "idle"; self.work_cycles = 0;
        self.total_seconds = WORK_MINUTES * 60; self._update_label_text()
    def update_display(self):
        self.total_seconds -= 1; self._update_label_text()
        if self.total_seconds < 0: self.timer.stop(); self._next_cycle()
    def _update_label_text(self): mins, secs = divmod(self.total_seconds, 60); self.time_label.setText(f"{mins:02}:{secs:02}")
    def _next_cycle(self):
        if self.state == "work":
            self.work_cycles += 1
            if self.work_cycles % 4 == 0: self.state = "long_break"; self.total_seconds = LONG_BREAK_MINUTES * 60
            else: self.state = "short_break"; self.total_seconds = SHORT_BREAK_MINUTES * 60
        else: self.state = "work"; self.total_seconds = WORK_MINUTES * 60
        self._update_label_text(); self.start_timer()


class TaskWidgetCompact(QWidget):
    """Widget Nhiệm vụ phiên bản "một dòng"."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(5)
        
        self.task_combo = QComboBox()
        self.task_combo.setMinimumWidth(120)
        layout.addWidget(self.task_combo)
        
        self.add_button = QPushButton("+"); self.add_button.setFixedSize(28, 28); layout.addWidget(self.add_button)
        self.delete_button = QPushButton("−"); self.delete_button.setFixedSize(28, 28); layout.addWidget(self.delete_button)

        self.add_button.clicked.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)
        
    def add_task(self):
        # Tạo QInputDialog và đặt stylesheet cho nó
        dialog = QInputDialog(self)
        dialog.setStyleSheet("QLineEdit { color: black; }") # Đặt màu chữ cho QLineEdit bên trong
        text, ok = dialog.getText(self, "Thêm Nhiệm vụ mới", "Tên nhiệm vụ:")
        
        if ok and text: self.task_combo.addItem(text); self.task_combo.setCurrentText(text)
    def delete_task(self):
        if self.task_combo.currentIndex() == -1: return
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa nhiệm vụ '{self.task_combo.currentText()}'?")
        if reply == QMessageBox.Yes: self.task_combo.removeItem(self.task_combo.currentIndex())


class FocusToolbar(QWidget):
    """Cửa sổ nổi chính, có thể chuyển đổi giữa ảnh GIF và thanh công cụ."""
    def __init__(self):
        super().__init__()
        self.is_expanded, self.drag_position = False, None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("FocusToolbar"); 
        # self.setStyleSheet(FOCUS_STYLESHEET)
        
        self.main_container = QWidget(); 
        self.main_container.setObjectName("MainContainer")
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0); 
        self.main_layout.setSpacing(10)
        
        window_layout = QHBoxLayout(self); 
        window_layout.setContentsMargins(0,0,0,0)
        window_layout.addWidget(self.main_container)

        self.toggle_button = QPushButton("🎯"); 
        self.toggle_button.setObjectName("ToggleButton"); 
        self.toggle_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self.toggle_button.clicked.connect(self.toggle_animation)

        self.collapsible_container = QWidget(); 
        self.collapsible_container.setObjectName("CollapsibleContainer")
        container_layout = QHBoxLayout(self.collapsible_container); 
        container_layout.setContentsMargins(5,0,5,0); 
        container_layout.setSpacing(5)
        
        self.task_widget = TaskWidgetCompact(); # Widget Nhiệm vụ phiên bản "một dòng"
        container_layout.addWidget(self.task_widget)


        line = QFrame(); 
        line.setFrameShape(QFrame.VLine) # Đường thẳng dọc
        line.setFrameShadow(QFrame.Plain) # Không đổ bóng
        container_layout.addWidget(line)

        self.pomodoro_widget = PomodoroWidgetCompact();  # Widget Pomodoro phiên bản "một dòng"
        container_layout.addWidget(self.pomodoro_widget)
        
        self.expanded_width = self.collapsible_container.sizeHint().width()+10
        self.collapsible_container.setMaximumWidth(0)
        
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.collapsible_container)
        self.main_layout.addStretch(1)  # Đẩy các thành phần sang bên trái
        
    def toggle_animation(self):
        content_end_width = self.expanded_width if not self.is_expanded else 0
        window_end_width = BUTTON_SIZE + content_end_width
        
        self.anim_content = QPropertyAnimation(self.collapsible_container, b"maximumWidth")
        self.anim_content.setDuration(ANIMATION_DURATION); 
        self.anim_content.setEndValue(content_end_width); 
        self.anim_content.setEasingCurve(QEasingCurve.InOutCubic) # Hiệu ứng easing
        
        self.anim_window = QPropertyAnimation(self.main_container, b"minimumWidth")
        self.anim_window.setDuration(ANIMATION_DURATION); 
        self.anim_window.setEndValue(window_end_width); 
        self.anim_window.setEasingCurve(QEasingCurve.InOutCubic) # Hiệu ứng easing
        
        self.anim_content.start(); 
        self.anim_window.start()
        self.is_expanded = not self.is_expanded

    def mousePressEvent(self, event):
        """ This method is called when a mouse button is pressed. [2] """
        if event.button() == Qt.LeftButton:
            print("Mouse pressed on toolbar")
            # Calculate the offset of the mouse click from the window's top-left corner.
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        print("Mouse moved on toolbar")
        print(self.drag_position)
        """ This method is called when the mouse is moved while a button is held down. [2] """
        if event.buttons() == Qt.LeftButton:
            # Ensure the drag position is valid.
            if self.drag_position is None:
                print("Drag position is None, cannot move toolbar.")
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            else:
                print(f"Moving toolbar to {event.globalPosition().toPoint() - self.drag_position}")
            # Move the window to the new global mouse position, adjusted by the offset.
            print(event.globalPosition().toPoint())
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept() 
            
    def mouseReleaseEvent(self, event):
        print("Mouse released on toolbar")
        """ This method is called when a mouse button is released. [2] """
        # Reset the drag position to stop the move.
        self.drag_position = None
        event.accept()
        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = QAction("Thoát", self)
        quit_action.triggered.connect(QCoreApplication.instance().quit)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 1. Tải stylesheet từ qdarktheme (dùng API cũ để tương thích)
    base_stylesheet = qdarktheme.load_stylesheet('light') # 'light' hoặc 'dark'
    
    # 2. Nối stylesheet tùy chỉnh của bạn vào
    combined_stylesheet = base_stylesheet + CUSTOM_STYLESHEET
    
    # 3. Áp dụng stylesheet KẾT HỢP cho toàn bộ ứng dụng
    app.setStyleSheet(combined_stylesheet)
    toolbar = FocusToolbar()
    toolbar.show()
    sys.exit(app.exec())
