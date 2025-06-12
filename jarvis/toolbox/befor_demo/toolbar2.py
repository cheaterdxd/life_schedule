# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QMenu
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QMouseEvent

# --- Constants and Stylesheet (unchanged) ---
BUTTON_SIZE = 40
SPACING = 10
ANIMATION_DURATION = 800
FLOATING_TOOLBAR_STYLESHEET = f""" 
    /* --- Container chính của toolbar --- */
    #FloatingToolbar {{
        /* background-color: rgba(44, 62, 80, 0.5);  Màu tối, hơi trong suốt */
        border-radius: {BUTTON_SIZE / 2}px; /* Để tạo hình tròn */
    }}

    /* --- Kiểu dáng chung cho nút tròn --- */
    QPushButton.CircularButton {{
        background-color: #34495e ; /* Màu xám đậm */
        color: white;
        border: none;
        font-size: 16px;
        font-weight: bold;
        border-radius: {BUTTON_SIZE / 2}px;
    }}
    QPushButton.CircularButton:hover {{
        background-color: #4a627a; /* Màu xám sáng hơn khi hover */
    }}
    
    /* --- Kiểu dáng riêng cho nút Toggle chính --- */
    QPushButton#ToggleButton {{
        background-color: #e67e22; /* Màu cam */
    }}
    QPushButton#ToggleButton:hover {{
        background-color: #f39c12; /* Màu cam sáng hơn khi hover */
    }}
"""


class FloatingToolbar(QWidget):
    def __init__(self):
        super().__init__()
        self.is_expanded = False
        self.drag_position = None # This variable will store the drag offset.

        # --- Window setup (unchanged) ---
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground) # Make the background translucent
        self.setObjectName("FloatingToolbar") # Set an object name for styling
        self.setStyleSheet(FLOATING_TOOLBAR_STYLESHEET) # Apply the stylesheet to the toolbar
        
        # --- Layout and buttons (unchanged) ---
        self.main_layout = QHBoxLayout(self) # This is the main layout for the toolbar
        self.main_layout.setContentsMargins(0, 0, 0, 0); # Set margins to 0 for a clean look
        self.main_layout.setSpacing(0) # Set spacing to 0 to avoid gaps between buttons

        # Create a container for the buttons
        self.buttons_container = QWidget() # This will hold the circular buttons
        self.buttons_layout = QHBoxLayout(self.buttons_container) # This is the layout for the buttons
        self.buttons_layout.setContentsMargins(SPACING, 0, 0, 0); # Set left margin to SPACING for the first button
        self.buttons_layout.setSpacing(SPACING) # Set spacing between buttons to SPACING
        button_definitions = [("⚙️", "Settings"), ("📁", "Open"), ("📊", "Stats"), ("🔔", "Alerts")]
        for icon, tooltip in button_definitions:
            self.buttons_layout.addWidget(self.create_circular_button(icon, tooltip))
        self.expanded_width = (BUTTON_SIZE * len(button_definitions)) + (SPACING * (len(button_definitions) + 1))
        self.buttons_container.setFixedWidth(0) # Set initial width to 0 for animation effect
        self.toggle_button = self.create_circular_button("☰", "Expand") # This is the main toggle button
        self.toggle_button.setObjectName("ToggleButton") # Set an object name for styling
        self.toggle_button.clicked.connect(self.toggle_animation) # Connect the toggle button to the animation method 
        self.main_layout.addWidget(self.toggle_button) # Add the toggle button to the main layout
        self.main_layout.addWidget(self.buttons_container) # Add the buttons container to the main layout
        self.main_layout.addStretch(1)  # Add stretch to push the buttons to the left side
        self.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)      # Set the fixed size of the toolbar to the size of the toggle button

    # --- Method to create circular buttons ---
    # This method creates a circular button with a given text and tooltip.
    def create_circular_button(self, text, tooltip):
        button = QPushButton(text)
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE); button.setToolTip(tooltip)
        button.setProperty("class", "CircularButton")
        button.clicked.connect(lambda: print(f"Clicked: '{tooltip}'"))
        return button
        
    def toggle_animation(self):
        # --- BƯỚC 1 & 2: Xác định trạng thái và tính toán kích thước đích ---
        
        # Nếu thanh công cụ đang thu gọn (is_expanded là False), thì kích thước đích
        # sẽ là chiều rộng đã tính toán trước đó (self.expanded_width).
        # Ngược lại, nếu đang mở rộng, kích thước đích sẽ là 0.
        end_width = self.expanded_width if not self.is_expanded else 0
        
        # Tính toán chiều rộng tổng thể của toàn bộ widget sau khi animation kết thúc.
        # Bằng chiều rộng của nút điều khiển (BUTTON_SIZE) cộng với chiều rộng của các nút con.
        total_end_width = BUTTON_SIZE + end_width

        # Cập nhật giao diện của nút điều khiển để cung cấp phản hồi cho người dùng.
        if not self.is_expanded:
            self.toggle_button.setText("⟨") # Đổi icon thành mũi tên "thu gọn"
            self.toggle_button.setToolTip("Thu gọn")
        else:
            self.toggle_button.setText("☰") # Đổi icon về dạng menu "mở rộng"
            self.toggle_button.setToolTip("Mở rộng")

        # --- BƯỚC 3: Tạo và cấu hình hiệu ứng (Animation) ---
        
        # Animation thứ nhất: Điều khiển kích thước của "hộp chứa" các nút con.
        # Nó sẽ thay đổi thuộc tính 'maximumWidth' của self.buttons_container.
        self.anim_container = QPropertyAnimation(self.buttons_container, b"maximumWidth")
        self.anim_container.setDuration(ANIMATION_DURATION) # Thời gian hiệu ứng
        self.anim_container.setEndValue(end_width) # Đặt kích thước đích
        self.anim_container.setEasingCurve(QEasingCurve.InOutCubic) # Kiểu hiệu ứng mượt mà

        # Animation thứ hai: Điều khiển kích thước của toàn bộ widget toolbar.
        # Điều này cần thiết để widget cha co giãn theo các nút con.
        self.anim_widget = QPropertyAnimation(self, b"minimumWidth")
        self.anim_widget.setDuration(ANIMATION_DURATION)
        self.anim_widget.setEndValue(total_end_width) # Đặt kích thước tổng thể đích
        self.anim_widget.setEasingCurve(QEasingCurve.InOutCubic)

        # Bắt đầu chạy cả hai hiệu ứng cùng một lúc.
        self.anim_container.start()
        self.anim_widget.start()
        
        # --- BƯỚC 4: Cập nhật lại trạng thái ---
        
        # Đảo ngược giá trị của biến trạng thái.
        # Nếu đang là True -> thành False, và ngược lại.
        self.is_expanded = not self.is_expanded


    # =========================================================================
    # === CODE FOR MOVING THE WIDGET AROUND ===
    # =========================================================================

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

    # --- Context menu (unchanged) ---
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        context_menu.addAction(quit_action)
        context_menu.exec(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolbar = FloatingToolbar()
    toolbar.show()
    sys.exit(app.exec())
