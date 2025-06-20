from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt

class FramelessDialog(QDialog):
    """
    Base class cho dialog không viền, đơn giản không có animation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Loại bỏ window frame và title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        # Thiết lập màu nền và viền cho dialog
        self.setStyleSheet("""
            QDialog  {
                background-color: #819A91;
                border: 1px solid #d0d0d0;
                border-radius: 15px;
            }
        """)
