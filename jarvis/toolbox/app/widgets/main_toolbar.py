from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QMenu,
    QFrame,
)
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QSize
)
from PySide6.QtGui import QAction,QMouseEvent, QMovie
from app.constants import BUTTON_SIZE, ANIMATION_DURATION
from app.styles import GIF_PATH
from app.clickableLabel import ClickableLabel
from .pomodoro import PomodoroWidgetCompact
from .task import TaskWidgetCompact
from app.dashboard import DashboardWindow

class FocusToolbar(QWidget):
    """Cửa sổ nổi chính, có thể thu gọn/mở rộng."""

    def __init__(self):
        super().__init__()
        self.is_expanded, self.drag_position = False, None
        self.dashboard = None  # Biến để lưu cửa sổ Dashboard
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("FocusToolbar")
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        window_layout = QHBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.main_container)

        # Thay thế QPushButton bằng ClickableLabel
        self.toggle_label = ClickableLabel(self)
        self.toggle_label.setObjectName(
            "ToggleButton"
        )  # Đặt tên cho label để dễ dàng định dạng trong CSS
        self.toggle_label.setFixedSize(BUTTON_SIZE + 40, BUTTON_SIZE)
        self.toggle_label.clicked.connect(self.toggle_animation)

        # Tạo QMovie để hiển thị GIF
        self.movie = QMovie(GIF_PATH)  # Đảm bảo file này tồn tại
        if not self.movie.isValid():
            print("Lỗi: Không thể tải file waving_cat.gif")
            self.toggle_label.setText("🎯")  # Fallback về text nếu không có GIF
        else:
            self.toggle_label.setMovie(self.movie)
            self.movie.setScaledSize(
                QSize(BUTTON_SIZE + 40, BUTTON_SIZE)
            )  # Co giãn GIF vừa với label
            self.movie.start()  # Bắt đầu chạy ảnh động

        self.collapsible_container = QWidget()
        self.collapsible_container.setObjectName("CollapsibleContainer")
        container_layout = QHBoxLayout(self.collapsible_container)
        container_layout.setContentsMargins(5, 0, 5, 0)
        container_layout.setSpacing(5)

        self.task_widget = TaskWidgetCompact()
        container_layout.addWidget(self.task_widget)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        container_layout.addWidget(line)
        self.pomodoro_widget = PomodoroWidgetCompact()
        container_layout.addWidget(self.pomodoro_widget)
        self.expanded_width = self.collapsible_container.sizeHint().width() + 10
        self.collapsible_container.setMaximumWidth(0)

        self.main_layout.addWidget(self.toggle_label)
        self.main_layout.addWidget(self.collapsible_container)
        self.main_layout.addStretch(1)

    # def open_dashboard_window(self):
    #     """
    #     Hàm này sẽ được gọi khi nút ⚙️ được nhấn.
    #     Hiện tại nó chỉ in ra một thông báo để kiểm tra.
    #     Sau này, nó sẽ chứa logic để mở cửa sổ Dashboard.
    #     """
    #     print("Yêu cầu mở cửa sổ Dashboard!")
    #     self.dashboard = DashboardWindow()
    #     self.dashboard.show()

    def open_dashboard_window(self):
        # Nếu dashboard chưa tồn tại hoặc đã bị đóng, tạo mới
        if self.dashboard is None or not self.dashboard.isVisible():
            self.dashboard = DashboardWindow()
            # Khi dashboard bị đóng, không xóa đối tượng, chỉ ẩn đi
            self.dashboard.destroyed.connect(lambda: setattr(self, 'dashboard', None))
        self.dashboard.show()

    def toggle_animation(self):
        # Hàm này không có thay đổi, nó vẫn hoạt động như cũ
        content_end_width = self.expanded_width if not self.is_expanded else 0
        window_end_width = BUTTON_SIZE + 40 + content_end_width
        self.anim_content = QPropertyAnimation(
            self.collapsible_container, b"maximumWidth"
        )
        self.anim_content.setDuration(ANIMATION_DURATION)
        self.anim_content.setEndValue(content_end_width)
        self.anim_content.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_window = QPropertyAnimation(self.main_container, b"minimumWidth")
        self.anim_window.setDuration(ANIMATION_DURATION)
        self.anim_window.setEndValue(window_end_width)
        self.anim_window.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_content.start()
        self.anim_window.start()
        self.is_expanded = not self.is_expanded

    # --- Các hàm xử lý kéo-thả và menu (đã dọn dẹp) ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = QAction("Thoát", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        menu.exec(event.globalPos())
