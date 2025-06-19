from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class PanelWidget(QWidget):
    """
    Một widget panel nền đơn giản với màu sắc và văn bản theo phong cách tối giản.
    Được sử dụng làm vùng chứa hoặc placeholder trong layout.
    """
    def __init__(self, text):
        super().__init__()
        self.setAutoFillBackground(True) # Đặt thuộc tính tự động điền nền để QPalette hoạt động.

        MINIMALIST_BACKGROUND = "#F3F4F6" # Màu xám rất nhạt (gần trắng) cho nền.
        MINIMALIST_TEXT = "#374151"       # Màu xám đậm cho văn bản, tạo độ tương phản tốt.

        palette = self.palette() # Lấy QPalette hiện tại của widget.
        palette.setColor(QPalette.ColorRole.Window, QColor(MINIMALIST_BACKGROUND)) # Đặt màu nền.
        self.setPalette(palette) # Áp dụng palette đã chỉnh sửa cho widget.
        
        layout = QVBoxLayout(self) # Tạo một QVBoxLayout (layout dọc) cho widget.
        label = QLabel(text) # Tạo một QLabel để hiển thị văn bản.
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Căn văn bản của nhãn vào giữa.
        
        font = label.font() # Lấy đối tượng QFont hiện tại của nhãn.
        font.setPointSize(24) # Đặt cỡ chữ lớn hơn cho nhãn.
        label.setFont(font) # Áp dụng font đã chỉnh sửa cho nhãn.

        label_palette = label.palette() # Lấy QPalette của nhãn.
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(MINIMALIST_TEXT)) # Đặt màu văn bản của nhãn.
        label.setPalette(label_palette) # Áp dụng palette đã chỉnh sửa cho nhãn.
        
        layout.addWidget(label) # Thêm nhãn vào layout.
        self.setLayout(layout) # Đặt layout cho widget.
