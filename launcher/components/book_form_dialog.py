from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpinBox, QDialogButtonBox
from PySide6.QtCore import Qt

class BookFormDialog(QDialog):
    """
    Dialog cho phép người dùng nhập liệu để thêm sách mới hoặc cập nhật thông tin sách hiện có.
    """
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin sách" if book_data else "Thêm sách mới") # Đặt tiêu đề dialog.
        self.setMinimumWidth(400) # Đặt chiều rộng tối thiểu.
        self.book_data = book_data or {}

        layout = QVBoxLayout(self) # Tạo layout chính cho dialog.

        self.title_edit = QLineEdit(self.book_data.get('title', '')) # Tạo trường nhập Tên sách.
        self.author_edit = QLineEdit(self.book_data.get('author', '')) # Tạo trường nhập Tác giả.
        self.file_edit = QLineEdit(self.book_data.get('file_path', '')) # Tạo trường hiển thị đường dẫn file.
        self.file_button = QPushButton("...") # Nút để mở hộp thoại chọn file.
        self.file_button.setFixedSize(30, 22) # Đặt kích thước cố định cho nút chọn file.
        self.file_button.clicked.connect(self.select_file) # Kết nối nút chọn file với phương thức select_file.
        
        self.total_pages_spin = QSpinBox() # Tạo trường nhập Tổng số trang.
        self.total_pages_spin.setRange(1, 10000) # Đặt phạm vi giá trị.
        self.total_pages_spin.setValue(self.book_data.get('total_pages', 1)) # Đặt giá trị ban đầu.

        self.pages_read_spin = QSpinBox() # Tạo trường nhập Số trang đã đọc.
        self.pages_read_spin.setRange(0, 10000) # Đặt phạm vi giá trị.
        self.pages_read_spin.setValue(self.book_data.get('pages_read', 0)) # Đặt giá trị ban đầu.
        self.total_pages_spin.valueChanged.connect(self.update_pages_read_max) # Kết nối sự kiện thay đổi giá trị.
        
        from PySide6.QtWidgets import QFormLayout
        form_layout = QFormLayout() # Tạo QFormLayout để sắp xếp nhãn và trường nhập liệu.
        file_layout = QHBoxLayout() # Tạo layout ngang cho trường đường dẫn file.
        file_layout.addWidget(self.file_edit) # Thêm trường nhập đường dẫn file.
        file_layout.addWidget(self.file_button) # Thêm nút chọn file.
        
        form_layout.addRow("Tên sách:", self.title_edit) # Thêm hàng "Tên sách".
        form_layout.addRow("Tác giả:", self.author_edit) # Thêm hàng "Tác giả".
        form_layout.addRow("Đường dẫn file:", file_layout) # Thêm hàng "Đường dẫn file".
        form_layout.addRow("Tổng số trang:", self.total_pages_spin) # Thêm hàng "Tổng số trang".
        form_layout.addRow("Số trang đã đọc:", self.pages_read_spin) # Thêm hàng "Số trang đã đọc".
        
        layout.addLayout(form_layout) # Thêm form layout vào layout chính.

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel) # Tạo QDialogButtonBox với các nút Ok và Cancel.
        buttons.accepted.connect(self.accept) # Kết nối nút Accepted.
        buttons.rejected.connect(self.reject) # Kết nối nút Rejected.
        layout.addWidget(buttons) # Thêm hộp nút vào layout chính.

    def update_pages_read_max(self, value):
        """
        Cập nhật giá trị tối đa cho trường số trang đã đọc dựa trên tổng số trang.
        Đảm bảo số trang đã đọc không vượt quá tổng số trang.
        """
        self.pages_read_spin.setMaximum(value) # Đặt giá trị tối đa cho pages_read_spin.

    def select_file(self):
        """
        Mở hộp thoại chọn file và cập nhật đường dẫn file vào trường nhập liệu.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file sách") # Mở hộp thoại chọn file.
        if file_path:
            self.file_edit.setText(file_path) # Cập nhật đường dẫn file vào trường nhập liệu.

    def get_data(self):
        """
        Lấy dữ liệu đã nhập từ các trường form.
        """
        return {
            'title': self.title_edit.text(),
            'author': self.author_edit.text(),
            'file_path': self.file_edit.text(),
            'total_pages': self.total_pages_spin.value(),
            'pages_read': self.pages_read_spin.value(),
        }
