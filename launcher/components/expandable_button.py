import qtawesome as qta
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QParallelAnimationGroup, QAbstractAnimation, Signal

class ExpandableButtonWidget(QWidget):
    """
    Widget nút bấm có thể mở rộng/thu gọn với animation mượt mà.
    Chứa các nút chức năng phụ và phát ra signal khi nút thoát được yêu cầu.
    """
    exit_requested = Signal() # Khai báo một signal mới, sẽ được phát ra khi người dùng nhấn nút "Exit".

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("expandableWidget") # Đặt tên đối tượng để dễ dàng áp dụng stylesheet.
        self.is_expanded = False # Trạng thái hiện tại của nút: False (thu gọn), True (mở rộng).
        
        self.COLLAPSED_SIZE = 50 # Kích thước (chiều rộng và chiều cao) khi nút ở trạng thái thu gọn.
        self.ICON_SIZE = 28 # Kích thước của các icon bên trong nút.
        self.ANIMATION_DURATION = 350 # Thời gian animation (milliseconds) để mở rộng/thu gọn.

        # --- Thêm biến font_prefix để xác định prefix cho icon ---
        self.font_prefix = 'fa6s' # Đặt tiền tố Font Awesome 6 Solid làm mặc định.

        self.width_anim = None
        self.opacity_anim = None

        self._setup_style() # Thiết lập stylesheet và màu sắc cho widget.
        
        self.main_layout = QHBoxLayout(self) # Tạo layout chính cho widget.
        self.main_layout.setContentsMargins(10, 0, 10, 0) # Đặt lề nội dung.
        self.main_layout.setSpacing(10) # Khoảng cách giữa các widget.

        self.toggle_button = QPushButton() # Tạo nút chính để mở rộng/thu gọn.
        self.toggle_button.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE) # Đặt kích thước cố định cho nút toggle.
        self.toggle_button.setIconSize(QSize(self.ICON_SIZE - 4, self.ICON_SIZE - 4)) # Đặt kích thước icon cho nút toggle.
        self.toggle_button.clicked.connect(self.toggle_animation) # Kết nối sự kiện click.
        
        self.button_container = QWidget() # Tạo một container để chứa các nút chức năng phụ.
        self.button_container_layout = QHBoxLayout(self.button_container) # Tạo layout ngang cho container.
        self.button_container_layout.setContentsMargins(0, 0, 0, 0) # Đặt lề nội dung của container.
        self.button_container_layout.setSpacing(5) # Khoảng cách giữa các nút chức năng.

        self.opacity_effect = QGraphicsOpacityEffect(self.button_container) # Tạo hiệu ứng mờ dần/hiện dần.
        self.opacity_effect.setOpacity(0.0) # Ban đầu đặt độ mờ là 0 (trong suốt).
        self.button_container.setGraphicsEffect(self.opacity_effect) # Áp dụng hiệu ứng mờ cho container.
        self.button_container.hide() # Ban đầu ẩn container các nút chức năng.

        self._create_function_buttons() # Tạo và thêm các nút chức năng vào container.

        self.main_layout.addWidget(self.toggle_button) # Thêm nút toggle vào layout chính.
        self.main_layout.addWidget(self.button_container) # Thêm container nút chức năng vào layout chính.
        
        self._update_toggle_icon() # Cập nhật icon cho nút toggle dựa trên trạng thái hiện tại.
        self.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE) # Đặt kích thước cố định ban đầu cho toàn bộ widget.
        
        self.animation_group = QParallelAnimationGroup(self) # Tạo một nhóm animation song song.
        self.animation_group.finished.connect(self._on_animation_finished) # Kết nối sự kiện kết thúc.

    def _setup_style(self):
        """
        Thiết lập stylesheet (CSS của Qt) cho widget và định nghĩa các màu sắc.
        Sử dụng bảng màu Minimalism.
        """
        self.WIDGET_BG_COLOR = "#FFFFFF" # Màu nền của widget (trắng tinh).
        self.ICON_COLOR = "#4B5563"      # Màu mặc định của icon (xám đậm).
        self.ICON_HOVER_COLOR = "#111827" # Màu của icon khi di chuột qua (gần đen).
        
        self.setStyleSheet(f"""
            #expandableWidget {{
                background-color: {self.WIDGET_BG_COLOR};
                border: none;
                border-radius: {self.COLLAPSED_SIZE / 2}px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)

    def _create_function_buttons(self):
            """
            Tạo các nút chức năng phụ (Profile, Home, Discover, Bookmarks, Settings, Exit)
            và thêm chúng vào container, sử dụng font_prefix đã định nghĩa.
            """
            icons_config = [
                (f"{self.font_prefix}.circle-user", "Profile"), # Cập nhật icon user-circle -> circle-user
                (f"{self.font_prefix}.house", "Home"),          # Thêm icon Home
                (f"{self.font_prefix}.compass", "Discover"),
                (f"{self.font_prefix}.bookmark", "Bookmarks"),
                (f"{self.font_prefix}.gear", "Settings"),       # Cập nhật icon cog -> gear
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
                    pass

                self.button_container_layout.addWidget(button)
                
            self.EXPANDED_WIDTH = self.COLLAPSED_SIZE + self.button_container_layout.count() * (self.ICON_SIZE + 15)

    def _update_toggle_icon(self):
        """
        Cập nhật icon của nút toggle dựa trên trạng thái mở rộng/thu gọn, sử dụng font_prefix.
        """
        if self.is_expanded:
            icon_name = f"{self.font_prefix}.chevron-left"
        else:
            icon_name = f"{self.font_prefix}.chevron-right"
        
        icon = qta.icon(icon_name, color=self.ICON_COLOR, color_active=self.ICON_HOVER_COLOR)
        self.toggle_button.setIcon(icon)

    def toggle_animation(self):
        """
        Bắt đầu animation để mở rộng hoặc thu gọn nút.
        Sử dụng QParallelAnimationGroup để chạy đồng thời animation chiều rộng và opacity.
        """
        self.is_expanded = not self.is_expanded
        
        self.animation_group.clear()

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

        self.animation_group.addAnimation(self.width_anim)
        self.animation_group.addAnimation(self.opacity_anim)
        
        self._update_toggle_icon()
        self.animation_group.start()

    def _on_animation_finished(self):
        """
        Xử lý sau khi animation hoàn thành.
        Cố định kích thước cuối cùng và ẩn container nút nếu đang thu gọn.
        """
        if self.is_expanded:
            self.setFixedSize(self.EXPANDED_WIDTH, self.COLLAPSED_SIZE)
        else:
            self.button_container.hide()
            self.setFixedSize(self.COLLAPSED_SIZE, self.COLLAPSED_SIZE)
