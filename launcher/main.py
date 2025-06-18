import sys
from PySide6.QtWidgets import QApplication

# Import cửa sổ chính từ thư mục 'views'
from views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Tạo và hiển thị cửa sổ chính
    window = MainWindow()
    window.showFullScreen() 
    
    sys.exit(app.exec())
