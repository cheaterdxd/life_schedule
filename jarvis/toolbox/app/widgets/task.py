from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QInputDialog,
    QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal


class TaskWidgetCompact(QWidget):
    # Lớp này không có thay đổi
    dashboard_requested = Signal()


    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)


        self.task_combo = QComboBox()
        self.task_combo.setMinimumWidth(150)
        layout.addWidget(self.task_combo)


        # self.add_button = QPushButton("+")
        # self.add_button.setFont(QFont("Segoe UI Symbol", 16))
        # self.add_button.setFixedSize(28, 28)
        # layout.addWidget(self.add_button)
        # self.delete_button = QPushButton("−")
        # self.delete_button.setFont(QFont("Segoe UI Symbol", 16))
        # self.delete_button.setFixedSize(28, 28)
        # layout.addWidget(self.delete_button)
        # self.add_button.clicked.connect(self.add_task)
        # self.delete_button.clicked.connect(self.delete_task)


        self.open_dashboard_button = QPushButton("⚙️")
        self.open_dashboard_button.setFixedSize(30, 30)
        # Khi nút này được nhấn, nó sẽ phát ra tín hiệu dashboard_requested
        self.open_dashboard_button.clicked.connect(self.dashboard_requested.emit)
        layout.addWidget(self.open_dashboard_button)

    def add_task(self):
        dialog = QInputDialog(self)
        dialog.setStyleSheet("QLineEdit { color: black; }")
        text, ok = dialog.getText(self, "Thêm Nhiệm vụ mới", "Tên nhiệm vụ:")
        if ok and text:
            self.task_combo.addItem(text)
            self.task_combo.setCurrentText(text)

    def delete_task(self):
        if self.task_combo.currentIndex() == -1:
            return
        reply = QMessageBox.question(
            self, "Xác nhận", f"Xóa nhiệm vụ '{self.task_combo.currentText()}'?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.task_combo.removeItem(self.task_combo.currentIndex())
