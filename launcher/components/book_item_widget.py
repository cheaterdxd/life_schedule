from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

class BookItemWidget(QWidget):
    """
    Widget hiển thị thông tin của một cuốn sách trong danh sách.
    Bao gồm tên sách, tác giả và một thanh tiến độ.
    """
    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.book_data = book_data

        layout = QVBoxLayout() # Tạo layout dọc.
        layout.setContentsMargins(10, 5, 10, 5) # Đặt lề nội dung.
        layout.setSpacing(3) # Đặt khoảng cách giữa các widget.
        self.setLayout(layout)

        self.title_author_label = QLabel(f"<b>{book_data.get('title', 'N/A')}</b> - <i>{book_data.get('author', 'N/A')}</i>") # Tạo nhãn tên sách/tác giả.
        self.title_author_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # Căn chỉnh văn bản.
        
        self.progress_bar = QProgressBar() # Tạo thanh tiến độ.
        self.progress_bar.setMinimum(0) # Đặt giá trị tối thiểu.
        
        total_pages = book_data.get('total_pages', 1)
        if total_pages == 0:
            total_pages = 1
        
        self.progress_bar.setMaximum(total_pages) # Đặt giá trị tối đa.
        self.progress_bar.setValue(book_data.get('pages_read', 0)) # Đặt giá trị hiện tại.
        self.progress_bar.setTextVisible(True) # Cho phép hiển thị văn bản.
        self.progress_bar.setFormat(f"%p% ({book_data.get('pages_read', 0)}/{total_pages})") # Đặt định dạng văn bản.

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d0d0d0; /* Đường viền mỏng và nhẹ. */
                border-radius: 5px;       /* Bo tròn góc. */
                background-color: #e0e0e0; /* Nền màu xám nhạt cho phần chưa hoàn thành. */
                text-align: center;       /* Căn giữa văn bản. */
                color: #4B5563;           /* Màu chữ xám đậm. */
            }
            QProgressBar::chunk {
                background-color: #6B7280; /* Màu xám trung tính cho phần đã hoàn thành. */
                border-radius: 5px;       /* Bo tròn góc khớp với nền. */
            }
        """)
        layout.addWidget(self.title_author_label) # Thêm nhãn vào layout.
        layout.addWidget(self.progress_bar) # Thêm thanh tiến độ vào layout.
        # self.layout.addWidget(self.progress_bar) # Thêm thanh tiến độ vào layout.
