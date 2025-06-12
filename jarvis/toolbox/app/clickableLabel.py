from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
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

