from PySide6.QtWidgets import QMainWindow
from components.expandable_button import ExpandableButtonWidget
from utils.layout_loader import LayoutLoader

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng launcher.
    Nó sử dụng LayoutLoader để tạo và quản lý bố cục chính của màn hình.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimalist Launcher") # Đặt tiêu đề cho cửa sổ.

        loader = LayoutLoader()
        main_splitter = loader.create_layout(self) # Tạo splitter và các widget con của nó.

        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: black; /* Đặt màu nền của thanh handle là đen. */
            }
            QSplitter::handle:horizontal {
                width: 1px; /* Đặt chiều rộng cho thanh handle ngang. */
            }
            QSplitter::handle:vertical {
                height: 1px; /* Đặt chiều cao cho thanh handle dọc. */
            }
        """)
        
        self.setCentralWidget(main_splitter) # Đặt splitter làm widget trung tâm của cửa sổ chính.

        self.expandable_button = ExpandableButtonWidget(self) # Tạo nút chức năng mở rộng/thu gọn.
        self.expandable_button.exit_requested.connect(self.close) # Kết nối signal 'exit_requested'.

    def resizeEvent(self, event):
        """
        Ghi đè phương thức resizeEvent để đảm bảo nút chức năng luôn nằm ở góc dưới bên trái.
        """
        super().resizeEvent(event)
        margin = 20 # Đặt lề.
        button_height = self.expandable_button.sizeHint().height() # Lấy chiều cao của nút.
        
        x = margin # Tọa độ X: Cách mép trái một khoảng margin.
        y = self.height() - button_height - margin # Tọa độ Y: Cách mép dưới một khoảng margin.
        
        self.expandable_button.move(x, y) # Di chuyển nút chức năng đến vị trí đã tính toán.
