# -*- coding: utf-8 -*-
"""
Ví dụ về Thanh công cụ có thể Thu gọn/Mở rộng với các nút tròn.
Sử dụng PySide6, QPropertyAnimation và Qt Style Sheets.
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont

# --- Hằng số để dễ dàng tùy chỉnh ---
BUTTON_SIZE = 40  # Kích thước (chiều rộng và cao) của nút tròn
SPACING = 10      # Khoảng cách giữa các nút
ANIMATION_DURATION = 300 # Thời gian hiệu ứng (miligiây)

# --- Bảng kiểu dáng (Stylesheet) cho giao diện ---
TOOLBAR_STYLESHEET = f"""
    /* --- Container chính của toolbar --- */
    #ToolbarContainer {{
        background-color: #2c3e50;
        border-radius: {BUTTON_SIZE / 2}px;
    }}

    /* --- Kiểu dáng chung cho nút tròn --- */
    QPushButton#CircularButton {{
        background-color: #34495e;
        color: white;
        border: none;
        font-size: 16px;
        font-weight: bold;
        border-radius: {BUTTON_SIZE / 2}px; /* Đây là chìa khóa để tạo nút tròn */
    }}
    QPushButton#CircularButton:hover {{
        background-color: #4a627a;
    }}
    QPushButton#CircularButton:pressed {{
        background-color: #2a3a4a;
    }}

    /* --- Kiểu dáng riêng cho nút Toggle chính --- */
    QPushButton#ToggleButton {{
        background-color: #e67e22; /* Màu cam */
    }}
    QPushButton#ToggleButton:hover {{
        background-color: #f39c12;
    }}
"""

class CollapsibleToolbar(QWidget):
    """
    Một widget toolbar tùy chỉnh chứa các nút tròn
    và có thể thu gọn/mở rộng với hiệu ứng animation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = False # Trạng thái ban đầu là thu gọn

        # Thiết lập layout chính cho toàn bộ toolbar
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setObjectName("ToolbarContainer") # Đặt tên để áp dụng style

        # Tạo container cho các nút chức năng (phần sẽ được thu/mở)
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(SPACING, 0, 0, 0)
        self.buttons_layout.setSpacing(SPACING)

        # Danh sách các icon và tooltip cho các nút chức năng
        button_definitions = [
            ("⚙️", "Cài đặt"),
            ("📁", "Mở File"),
            ("📊", "Thống kê"),
            ("🔔", "Thông báo")
        ]

        # Tạo và thêm các nút chức năng vào layout của container
        for icon, tooltip in button_definitions:
            button = self.create_circular_button(icon, tooltip)
            self.buttons_layout.addWidget(button)

        # Tính toán chiều rộng tối đa khi mở rộng
        self.expanded_width = (BUTTON_SIZE * len(button_definitions)) + (SPACING * (len(button_definitions) + 1))
        
        # Đặt chiều rộng ban đầu của container là 0 để nó bị ẩn
        self.buttons_container.setFixedWidth(0)

        # Tạo nút chính để điều khiển việc thu/mở
        self.toggle_button = self.create_circular_button("☰", "Mở rộng")
        self.toggle_button.setObjectName("ToggleButton") # Đặt tên riêng để có style khác
        self.toggle_button.clicked.connect(self.toggle_animation)
        
        # Thêm các thành phần vào layout chính
        # Đặt nút toggle bên trái, các nút chức năng bên phải
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.buttons_container)

    def create_circular_button(self, text, tooltip=""):
        """Hàm trợ giúp để tạo một nút tròn nhất quán."""
        button = QPushButton(text, self)
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setObjectName("CircularButton") # Áp dụng style chung
        button.setToolTip(tooltip)
        # Kết nối sự kiện click của nút này tới một hàm xử lý (tùy chọn)
        button.clicked.connect(lambda: print(f"Bạn đã nhấp vào nút: '{tooltip}'"))
        return button

    def toggle_animation(self):
        """Kích hoạt hiệu ứng animation để mở rộng hoặc thu gọn toolbar."""
        # Xác định chiều rộng bắt đầu và kết thúc dựa trên trạng thái hiện tại
        start_width = self.buttons_container.width()
        end_width = self.expanded_width if not self.is_expanded else 0
        
        # Cập nhật trạng thái và icon của nút toggle
        if not self.is_expanded:
            self.toggle_button.setText("⟨") # Mũi tên chỉ sang trái
            self.toggle_button.setToolTip("Thu gọn")
        else:
            self.toggle_button.setText("☰") # Biểu tượng menu
            self.toggle_button.setToolTip("Mở rộng")
            
        # Tạo và cấu hình animation
        self.animation = QPropertyAnimation(self.buttons_container, b"maximumWidth")
        self.animation.setDuration(ANIMATION_DURATION)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic) # Hiệu ứng mượt mà
        
        # Bắt đầu animation
        self.animation.start()
        
        # Đảo ngược trạng thái
        self.is_expanded = not self.is_expanded

class MainWindow(QMainWindow):
    """Cửa sổ chính để chứa và hiển thị toolbar."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Collapsible Circular Toolbar Demo")
        self.setGeometry(300, 300, 600, 400)

        # Tạo widget trung tâm và layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Thêm một nhãn hướng dẫn
        info_label = QLabel("Nhấp vào nút màu cam để mở rộng hoặc thu gọn thanh công cụ.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 14))

        # Tạo và thêm toolbar vào layout
        self.toolbar = CollapsibleToolbar()
        
        # Sử dụng một layout phụ để căn chỉnh toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.toolbar)
        toolbar_layout.addStretch() # Đẩy toolbar về phía bên trái

        layout.addLayout(toolbar_layout)
        layout.addWidget(info_label)
        layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(TOOLBAR_STYLESHEET) # Áp dụng stylesheet cho toàn bộ ứng dụng
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
