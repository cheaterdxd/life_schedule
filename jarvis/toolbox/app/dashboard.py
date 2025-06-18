from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTableWidget, QPushButton, QHeaderView, QTableWidgetItem, QInputDialog
from .data_manager import load_tasks, save_tasks
from app.data_manager import load_activity_log

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard - Quản lý Nhiệm vụ & Thống kê")
        self.setMinimumSize(600, 400)

        # Tạo tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab 1: Quản lý nhiệm vụ
        self.task_tab = QWidget()
        self.task_layout = QVBoxLayout(self.task_tab)
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["Tên nhiệm vụ", "Trạng thái", "Ngày tạo"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.task_layout.addWidget(self.task_table)

        self.add_button = QPushButton("Thêm nhiệm vụ")
        self.add_button.clicked.connect(self.add_task)
        self.task_layout.addWidget(self.add_button)

        self.del_button = QPushButton("Xóa nhiệm vụ")
        self.del_button.clicked.connect(self.delete_task)
        self.task_layout.addWidget(self.del_button)

        self.edit_button = QPushButton("Sửa nhiệm vụ")
        self.edit_button.clicked.connect(self.edit_task)
        self.task_layout.addWidget(self.edit_button)

        self.complete_button = QPushButton("Hoàn thành")
        self.complete_button.clicked.connect(self.mark_complete)
        self.task_layout.addWidget(self.complete_button)

        self.tab_widget.addTab(self.task_tab, "Nhiệm vụ")

        # Tab 2: Thống kê (để trống, sẽ phát triển sau)
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        self.tab_widget.addTab(self.stats_tab, "Thống kê")

        # Load dữ liệu
        self.load_tasks()

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(["Task", "Thời gian (phút)", "Ngày"])
        self.stats_layout.addWidget(self.stats_table)
        self.load_stats()

    def load_tasks(self):
        tasks = load_tasks()
        self.task_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.task_table.setItem(i, 0, QTableWidgetItem(task.get("name", "")))
            self.task_table.setItem(i, 1, QTableWidgetItem(task.get("status", "Chưa hoàn thành")))
            self.task_table.setItem(i, 2, QTableWidgetItem(task.get("created_at", "")))

    def add_task(self):
        name, ok = QInputDialog.getText(self, "Thêm nhiệm vụ", "Tên nhiệm vụ:")
        if ok and name:
            tasks = load_tasks()
            new_task = {"name": name, "status": "Chưa hoàn thành", "created_at": "2023-01-01"}  # TODO: Thêm ngày thực tế
            tasks.append(new_task)
            save_tasks(tasks)
            self.load_tasks()

    def delete_task(self):
        row = self.task_table.currentRow()
        if row >= 0:
            tasks = load_tasks()
            tasks.pop(row)
            save_tasks(tasks)
            self.load_tasks()
    def edit_task(self):
        row = self.task_table.currentRow()
        if row >= 0:
            tasks = load_tasks()
            name, ok = QInputDialog.getText(self, "Sửa nhiệm vụ", "Tên mới:", text=tasks[row]["name"])
            if ok and name:
                tasks[row]["name"] = name
                save_tasks(tasks)
                self.load_tasks()

    def mark_complete(self):
        row = self.task_table.currentRow()
        if row >= 0:
            tasks = load_tasks()
            tasks[row]["status"] = "Đã hoàn thành"
            # TODO: Thêm ngày hoàn thành nếu cần
            save_tasks(tasks)
            self.load_tasks()
            
    def load_stats(self):
        logs = load_activity_log()
        self.stats_table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            self.stats_table.setItem(i, 0, QTableWidgetItem(log["task"]))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(log["duration"])))
            self.stats_table.setItem(i, 2, QTableWidgetItem(log["date"]))
