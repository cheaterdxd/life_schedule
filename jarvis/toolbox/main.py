# main.py

import sys
from PySide6.QtWidgets import QApplication
from app.widgets.main_toolbar import FocusToolbar
import qdarktheme
from app.styles import CUSTOM_STYLESHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_stylesheet = qdarktheme.load_stylesheet("light")
    combined_stylesheet = base_stylesheet + CUSTOM_STYLESHEET
    app.setStyleSheet(combined_stylesheet)
    # Tạo và hiển thị thanh toolbar
    toolbar = FocusToolbar()
    toolbar.show()
    
    sys.exit(app.exec())
