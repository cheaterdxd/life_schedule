from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpinBox, QDialogButtonBox, QFormLayout
from PySide6.QtCore import Qt
from components.frameless_dialog import FramelessDialog
class BookFormDialog(FramelessDialog):
    """
    Dialog cho phép người dùng nhập liệu để thêm sách mới hoặc cập nhật thông tin sách hiện có.
    Kế thừa từ FramelessDialog để có giao diện tối giản không viền.
    """
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin sách" if book_data else "Thêm sách mới")
        self.setMinimumWidth(400) # Đặt chiều rộng tối thiểu.
        self.book_data = book_data or {}

        # Áp dụng stylesheet cho input fields với bo tròn
        self.setStyleSheet(self.styleSheet() + """
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: #f8f9fa;
                color: #374151;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4B5563;
                background-color: white;
            }
            QSpinBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: #f8f9fa;
                color: #374151;
                font-size: 14px;
            }
            QSpinBox:focus {
                border: 1px solid #4B5563;
                background-color: white;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                color: #374151;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #4B5563;
            }
            QLabel {
                color: #374151;
                font-weight: 500;
            }
        """)

        layout = QVBoxLayout(self) # Tạo layout chính cho dialog.
        layout.setContentsMargins(20, 20, 20, 20) # Thêm margin cho dialog.

        self.title_edit = QLineEdit(self.book_data.get('title', '')) # Tạo trường nhập Tên sách.
        self.author_edit = QLineEdit(self.book_data.get('author', '')) # Tạo trường nhập Tác giả.
        self.file_edit = QLineEdit(self.book_data.get('file_path', '')) # Tạo trường hiển thị đường dẫn file.
        self.file_button = QPushButton("...") # Nút để mở hộp thoại chọn file.
        self.file_button.setFixedSize(40, 32) # Đặt kích thước cho nút chọn file.
        self.file_button.clicked.connect(self.select_file) # Kết nối nút chọn file.
        
        self.total_pages_spin = QSpinBox() # Tạo trường nhập Tổng số trang.
        self.total_pages_spin.setRange(1, 10000) # Đặt phạm vi giá trị.
        self.total_pages_spin.setValue(self.book_data.get('total_pages', 1)) # Đặt giá trị ban đầu.

        self.pages_read_spin = QSpinBox() # Tạo trường nhập Số trang đã đọc.
        self.pages_read_spin.setRange(0, 10000) # Đặt phạm vi giá trị.
        self.pages_read_spin.setValue(self.book_data.get('pages_read', 0)) # Đặt giá trị ban đầu.
        self.total_pages_spin.valueChanged.connect(self.update_pages_read_max) # Kết nối sự kiện thay đổi giá trị.
        
        form_layout = QFormLayout() # Tạo QFormLayout để sắp xếp nhãn và trường nhập liệu.
        form_layout.setSpacing(15) # Tăng khoảng cách giữa các hàng.
        
        file_layout = QHBoxLayout() # Tạo layout ngang cho trường đường dẫn file.
        file_layout.addWidget(self.file_edit) # Thêm trường nhập đường dẫn file.
        file_layout.addWidget(self.file_button) # Thêm nút chọn file.
        
        form_layout.addRow("Tên sách:", self.title_edit) # Thêm hàng "Tên sách".
        form_layout.addRow("Tác giả:", self.author_edit) # Thêm hàng "Tác giả".
        form_layout.addRow("Đường dẫn file:", file_layout) # Thêm hàng "Đường dẫn file".
        form_layout.addRow("Tổng số trang:", self.total_pages_spin) # Thêm hàng "Tổng số trang".
        form_layout.addRow("Số trang đã đọc:", self.pages_read_spin) # Thêm hàng "Số trang đã đọc".
        
        layout.addLayout(form_layout) # Thêm form layout vào layout chính.

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel) # Tạo QDialogButtonBox.
        buttons.accepted.connect(self.accept) # Kết nối nút OK.
        buttons.rejected.connect(self.reject) # Kết nối nút Cancel.
        layout.addWidget(buttons) # Thêm hộp nút vào layout chính.

    def update_pages_read_max(self, value):
        """Cập nhật giá trị tối đa cho trường số trang đã đọc."""
        self.pages_read_spin.setMaximum(value)

    def select_file(self):
        """Mở hộp thoại chọn file và cập nhật đường dẫn file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file sách")
        if file_path:
            self.file_edit.setText(file_path)

    def get_data(self):
        """Lấy dữ liệu đã nhập từ các trường form."""
        return {
            'title': self.title_edit.text(),
            'author': self.author_edit.text(),
            'file_path': self.file_edit.text(),
            'total_pages': self.total_pages_spin.value(),
            'pages_read': self.pages_read_spin.value(),
        }
