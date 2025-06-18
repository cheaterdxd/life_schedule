from PySide6.QtWidgets import QMainWindow, QSplitter

# Import các component từ thư mục 'components'
from components.panel_widget import PanelWidget
from components.expandable_button import ExpandableButtonWidget
from PySide6.QtCore import Qt
# --- Lớp cửa sổ chính của ứng dụng ---
class MainWindow(QMainWindow):
    # Trong lớp LauncherWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimalist Launcher") # Đổi tên cho phù hợp

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tạo panel mà không cần truyền màu nữa
        panel1 = PanelWidget("Workspace 1")
        panel2 = PanelWidget("Main View")
        panel3 = PanelWidget("Details")
        
        main_splitter.addWidget(panel1)
        main_splitter.addWidget(panel2)
        main_splitter.addWidget(panel3)
        main_splitter.setSizes([200, 400, 200])
        
        # Loại bỏ đường viền của QSplitter handle
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """)
        main_splitter.setHandleWidth(1) # Làm cho thanh chia mỏng hơn

        self.setCentralWidget(main_splitter)
        
        self.expandable_button = ExpandableButtonWidget(self)
        self.expandable_button.exit_requested.connect(self.close)


    # Ghi đè sự kiện resize để luôn giữ nút ở góc dưới bên phải
    def resizeEvent(self, event):
        """Đảm bảo nút chức năng luôn ở góc dưới BÊN TRÁI."""
        super().resizeEvent(event)
        margin = 20
        
        # Chiều cao nút cần được lấy từ sizeHint() vì kích thước có thể đang trong animation
        button_height = self.expandable_button.sizeHint().height() 
        
        # Sửa logic tính tọa độ x để căn lề trái
        x = margin
        y = self.height() - button_height - margin
        
        self.expandable_button.move(x, y)

