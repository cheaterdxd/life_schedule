import qtawesome as qta
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QParallelAnimationGroup, QAbstractAnimation, Signal
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGraphicsOpacityEffect


class ExpandableButtonWidget(QWidget):
    exit_requested = Signal()  # Tín hiệu để thông báo khi animation kết thúc
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_prefix = 'fa6s'  # Sử dụng Font Awesome 5 Regular (outline)
        self.setObjectName("expandableWidget")
        self.is_expanded = False
        self.width_animation = None
        self.height_animation = None
        self.COLLAPSED_SIZE = 50
        self.ICON_SIZE = 28
        self.ANIMATION_DURATION:int = 700 # Tăng nhẹ thời gian cho mượt hơn
        
        self._setup_style()
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 0, 10, 0) # Thêm margin phải
        self.main_layout.setSpacing(10)

        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE)
        self.toggle_button.setIconSize(QSize(self.ICON_SIZE - 4, self.ICON_SIZE - 4))
        self.toggle_button.clicked.connect(self.toggle_animation)
        
        self.button_container = QWidget()
        self.button_container_layout = QHBoxLayout(self.button_container)
        self.button_container_layout.setContentsMargins(0, 0, 0, 0)
        self.button_container_layout.setSpacing(5)

        # --- NÂNG CẤP ANIMATION ---
        # 1. Thêm hiệu ứng opacity cho container nút
        self.opacity_effect = QGraphicsOpacityEffect(self.button_container)
        self.opacity_effect.setOpacity(0.0) # Ban đầu trong suốt
        self.button_container.setGraphicsEffect(self.opacity_effect)
        self.button_container.hide() # Vẫn ẩn để không chiếm layout

        self._create_function_buttons()

        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.button_container)
        
        self._update_toggle_icon()
        self.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE)
        
        # 2. Tạo một nhóm animation song song
        self.animation_group = QParallelAnimationGroup(self)
        self.animation_group.finished.connect(self._on_animation_finished)


    def _setup_style(self):
        # Màu sắc từ bảng màu tối giản
        self.WIDGET_BG_COLOR = "#FFFFFF"       # Nền trắng tinh
        self.ICON_COLOR = "#4B5563"          # Icon màu xám đậm
        self.ICON_HOVER_COLOR = "#111827"    # Icon chuyển sang gần đen khi hover
        
        self.setStyleSheet(f"""
            #expandableWidget {{
                background-color: {self.WIDGET_BG_COLOR};
                border: none; /* Loại bỏ đường viền để có flat style */
                border-radius: {self.COLLAPSED_SIZE / 2}px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)

    # 2. Thay thế hàm _create_function_buttons
    def _create_function_buttons(self):

        # Sử dụng qtawesome để tạo icon outline
        # 'fa5r' là Font Awesome 5 Regular (thường là outline)
        icons_config = [
            (f"{self.font_prefix}.circle-user", "Profile"),
            (f"{self.font_prefix}.house", "Home"),
            (f"{self.font_prefix}.compass", "Discover"),
            (f"{self.font_prefix}.bookmark", "Bookmarks"),
            (f"{self.font_prefix}.gear", "Settings"),
            (f"{self.font_prefix}.power-off", "Exit")
        ]
        
        for icon_name, tooltip in icons_config:
            icon = qta.icon(icon_name, color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
            button = QPushButton(icon, "")
            button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
            button.setFixedSize(self.ICON_SIZE + 10, self.ICON_SIZE + 10)
            button.setToolTip(tooltip)
            if tooltip == "Exit":
                button.clicked.connect(self.exit_requested.emit)
            else:
                # Bạn có thể thêm xử lý cho các nút khác ở đây trong tương lai
                # Ví dụ: button.clicked.connect(lambda t=tooltip: print(f"{t} clicked"))
                pass
            self.button_container_layout.addWidget(button)
            
        self.EXPANDED_WIDTH = self.COLLAPSED_SIZE + self.button_container_layout.count() * (self.ICON_SIZE + 15)

    # 3. Thay thế hàm _update_toggle_icon
    def _update_toggle_icon(self):
        # Sử dụng icon chevron đơn giản, phù hợp với flat style
        if self.is_expanded:
            icon_name = f'{self.font_prefix}.chevron-left'
        else:
            icon_name = f'{self.font_prefix}.chevron-right'

        icon = qta.icon(icon_name, color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
        self.toggle_button.setIcon(icon)

    def toggle_animation(self):
        self.is_expanded = not self.is_expanded
        
        self.animation_group.clear()

        # SỬA LỖI: Gán vào thuộc tính của instance thay vì biến cục bộ
        self.width_anim = QPropertyAnimation(self, b"minimumWidth")
        self.width_anim.setDuration(self.ANIMATION_DURATION)
        self.width_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(int(self.ANIMATION_DURATION / 2))
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        if self.is_expanded:
            self.button_container.show()
            self.width_anim.setStartValue(self.width())
            self.width_anim.setEndValue(self.EXPANDED_WIDTH)
            self.opacity_anim.setStartValue(0.0)
            self.opacity_anim.setEndValue(1.0)
        else:
            self.width_anim.setStartValue(self.width())
            self.width_anim.setEndValue(self.COLLAPSED_SIZE)
            self.opacity_anim.setStartValue(1.0)
            self.opacity_anim.setEndValue(0.0)

        # Thêm các thuộc tính animation vào group
        self.animation_group.addAnimation(self.width_anim)
        self.animation_group.addAnimation(self.opacity_anim)
        
        self._update_toggle_icon()
        self.animation_group.start()



    def _on_animation_finished(self):
        # Cố định kích thước cuối cùng và ẩn container nếu cần
        if self.is_expanded:
            self.setFixedSize(self.EXPANDED_WIDTH, self.COLLAPSED_SIZE)
        else:
            self.button_container.hide() # Ẩn đi sau khi đã mờ hẳn
            self.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE)

