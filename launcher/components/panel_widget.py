from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class PanelWidget(QWidget):
# Trong lớp PanelWidget
    def __init__(self, text):
        super().__init__()
        self.setAutoFillBackground(True)

        # Bảng màu tối giản (Minimalist Palette)
        MINIMALIST_BACKGROUND = "#F3F4F6" # Màu xám rất nhạt (Off-white/Light Gray)
        MINIMALIST_TEXT = "#374151"       # Màu xám đậm cho chữ

        # Thiết lập màu nền
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(MINIMALIST_BACKGROUND))
        self.setPalette(palette)
        
        # Thiết lập nhãn với màu chữ mới
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = label.font()
        font.setPointSize(24)
        label.setFont(font)

        # Đặt màu cho chữ
        label_palette = label.palette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(MINIMALIST_TEXT))
        label.setPalette(label_palette)
        
        layout.addWidget(label)
        self.setLayout(layout)
