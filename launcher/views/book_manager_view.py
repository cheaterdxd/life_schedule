# Trong views/book_manager_view.py, tìm và thay thế toàn bộ lớp BookManagerView:

import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QDialog
from PySide6.QtCore import Qt, QSize

from components.book_item_widget import BookItemWidget
from components.book_form_dialog import BookFormDialog
from data.data_manager import DataManager

class BookManagerView(QWidget):
    """
    View chính cho trình quản lý sách.
    Bao gồm thanh công cụ (Thêm, Xóa, Cập nhật) và danh sách hiển thị sách.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.books = self.data_manager.load_books()

        self.ICON_COLOR = "#4B5563"      # Màu mặc định của icon.
        self.ICON_HOVER_COLOR = "#111827" # Màu của icon khi di chuột qua.
        self.BUTTON_ICON_SIZE = 15      # Kích thước icon bên trong nút.
        self.BUTTON_ROUND_SIZE = 20      # Kích thước cố định của nút tròn (chiều rộng và chiều cao).

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 0, 5) # 10px từ mép trái, 0px cho các mép còn lại.

        # Nút "Thêm" sách
        add_icon = qta.icon('fa6s.plus', color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
        self.add_button = QPushButton(add_icon, "")
        self.add_button.setToolTip("Thêm sách mới")
        self.add_button.setIconSize(QSize(self.BUTTON_ICON_SIZE, self.BUTTON_ICON_SIZE))
        self.add_button.setFixedSize(self.BUTTON_ROUND_SIZE, self.BUTTON_ROUND_SIZE) # Đặt kích thước cố định cho nút tròn.

        # Nút "Xóa" sách
        delete_icon = qta.icon('fa6s.trash-can', color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
        self.delete_button = QPushButton(delete_icon, "")
        self.delete_button.setToolTip("Xóa sách đã chọn")
        self.delete_button.setIconSize(QSize(self.BUTTON_ICON_SIZE, self.BUTTON_ICON_SIZE))
        self.delete_button.setFixedSize(self.BUTTON_ROUND_SIZE, self.BUTTON_ROUND_SIZE) # Đặt kích thước cố định cho nút tròn.

        # Nút "Cập nhật" sách
        update_icon = qta.icon('fa6s.pen', color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
        self.update_button = QPushButton(update_icon, "")
        self.update_button.setToolTip("Cập nhật thông tin sách đã chọn")
        self.update_button.setIconSize(QSize(self.BUTTON_ICON_SIZE, self.BUTTON_ICON_SIZE))
        self.update_button.setFixedSize(self.BUTTON_ROUND_SIZE, self.BUTTON_ROUND_SIZE) # Đặt kích thước cố định cho nút tròn.

        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addWidget(self.update_button)
        toolbar_layout.addStretch()

        # Cập nhật stylesheet cho QPushButton
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; /* Nền trong suốt. */
                border: 1px solid {self.ICON_COLOR}; /* Thêm viền outline mỏng, màu ICON_COLOR. */
                border-radius: {self.BUTTON_ROUND_SIZE / 2}px; /* Bo tròn góc để tạo hình tròn. */
                padding: 0px; /* Không có padding. */
            }}
            QPushButton:hover {{
                border: 1px solid {self.ICON_HOVER_COLOR}; /* Đổi màu viền khi hover. */
            }}
        """)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
                alternate-background-color: #F8F8F8;
            }
            QListWidget::item:selected {
                background-color: #E0E0E0;
                color: black;
            }
        """)

        layout.addLayout(toolbar_layout)
        layout.addWidget(self.list_widget)

        self.add_button.clicked.connect(self.add_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.update_button.clicked.connect(self.update_book)

        self.refresh_list()

    def refresh_list(self):
        """
        Xóa và hiển thị lại toàn bộ danh sách sách trong QListWidget.
        """
        self.list_widget.clear()
        for book in self.books:
            item = QListWidgetItem(self.list_widget)
            widget = BookItemWidget(book)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def add_book(self):
        """
        Mở dialog để thêm sách mới.
        Nếu dữ liệu được chấp nhận, thêm sách vào danh sách và lưu lại.
        """
        dialog = BookFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_book = dialog.get_data()
            self.books.append(new_book)
            self.data_manager.save_books(self.books)
            self.refresh_list()

    def delete_book(self):
        """
        Xóa sách đã chọn khỏi danh sách sau khi xác nhận từ người dùng.
        """
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Chưa chọn sách", "Vui lòng chọn một cuốn sách để xóa.")
            return

        book = self.books[current_row]
        reply = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn xóa '{book.get('title', '')}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.books.pop(current_row)
            self.data_manager.save_books(self.books)
            self.refresh_list()

    def update_book(self):
        """
        Mở dialog để cập nhật thông tin của sách đã chọn.
        Nếu dữ liệu được chấp nhận, cập nhật sách trong danh sách và lưu lại.
        """
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Chưa chọn sách", "Vui lòng chọn một cuốn sách để cập nhật.")
            return

        book = self.books[current_row]
        dialog = BookFormDialog(self, book)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_book = dialog.get_data()
            self.books[current_row] = updated_book
            self.data_manager.save_books(self.books)
            self.refresh_list()
