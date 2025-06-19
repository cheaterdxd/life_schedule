from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout
from PySide6.QtCore import Qt

from views.book_manager_view import BookManagerView
from components.panel_widget import PanelWidget

class BookManagerWorkspace(QWidget):
    """
    Workspace được chia thành hai phần: Trình quản lý sách ở trên và
    một placeholder cho To-do List ở dưới.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self) # Tạo layout chính cho workspace.
        main_layout.setContentsMargins(0, 0, 0, 0) # Đặt lề nội dung bằng 0.
        self.setLayout(main_layout) # Đặt layout cho widget.

        self.splitter = QSplitter(Qt.Orientation.Vertical) # Tạo QSplitter theo chiều dọc để chia không gian trên và dưới.

        self.book_manager_view = BookManagerView() # Phần trên: Trình quản lý sách.
        self.todo_placeholder = PanelWidget("To-do List (Placeholder)") # Phần dưới: Placeholder cho To-do List.

        self.splitter.addWidget(self.book_manager_view) # Thêm trình quản lý sách vào splitter.
        self.splitter.addWidget(self.todo_placeholder) # Thêm placeholder vào splitter.
        
        self.splitter.setSizes([400, 200]) # Thiết lập tỷ lệ kích thước ban đầu.

        main_layout.addWidget(self.splitter) # Thêm splitter vào layout chính của workspace.
