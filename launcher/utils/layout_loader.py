import os
from PySide6.QtWidgets import QSplitter, QWidget
from PySide6.QtCore import Qt

from views.book_manager_workspace import BookManagerWorkspace
from components.panel_widget import PanelWidget

class LayoutLoader:
    """
    Đọc file cấu hình views.config và xây dựng layout chính của ứng dụng một cách động.
    Cho phép thay đổi bố cục mà không cần sửa code.
    """
    def __init__(self, config_path='views.config'):
        self.config_path = config_path

    def parse_config(self):
        """
        Đọc và phân tích nội dung của file cấu hình.
        """
        if not os.path.exists(self.config_path):
            return Qt.Orientation.Horizontal, ['workspace', 'mainview', 'details'], [333, 333, 334] # Trả về cấu hình mặc định.

        orientation = Qt.Orientation.Horizontal
        panels = []
        ratios = []

        with open(self.config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                if line.startswith('-'):
                    orientation_str = line[1:].strip().lower()
                    if orientation_str == 'ngang':
                        orientation = Qt.Orientation.Vertical
                    elif orientation_str == 'dọc':
                        orientation = Qt.Orientation.Horizontal
                elif line.startswith('+'):
                    try:
                        panel_name, ratio_str = [p.strip() for p in line[1:].split(':')]
                        ratio_val = float(eval(ratio_str))
                        panels.append(panel_name)
                        ratios.append(ratio_val)
                    except (ValueError, SyntaxError):
                        print(f"Warning: Could not parse line: {line}") # In cảnh báo nếu không thể parse dòng.

        total_ratio = sum(ratios) if ratios else 1
        sizes = [int(1000 * r / total_ratio) for r in ratios] # Chuyển tỷ lệ thành các giá trị số nguyên.
        
        return orientation, panels, sizes

    def create_layout(self, parent=None):
        """
        Dựa trên cấu hình đã phân tích, tạo ra QSplitter và các widget con.
        """
        orientation, panel_names, sizes = self.parse_config()
        splitter = QSplitter(orientation, parent) # Tạo QSplitter với hướng đã xác định.

        for name in panel_names:
            widget = self._get_widget_by_name(name, parent) # Lấy widget tương ứng với tên.
            splitter.addWidget(widget) # Thêm widget vào splitter.

        if sizes:
            splitter.setSizes(sizes) # Áp dụng tỷ lệ kích thước cho các panel.
        return splitter

    def _get_widget_by_name(self, name, parent=None):
        """
        Ánh xạ tên panel từ cấu hình thành thể hiện của các lớp widget tương ứng.
        """
        name = name.lower().strip()
        if name in ('workspace', 'pannel1', 'panel1'):
            return BookManagerWorkspace(parent) # Trả về BookManagerWorkspace.
        if name in ('mainview', 'pannel2', 'panel2'):
            return PanelWidget("Main View") # Trả về PanelWidget cho "Main View".
        if name in ('details', 'pannel3', 'panel3'):
            return PanelWidget("Details") # Trả về PanelWidget cho "Details".
        
        return PanelWidget(f"Unknown: {name}") # Trường hợp không khớp tên nào.
