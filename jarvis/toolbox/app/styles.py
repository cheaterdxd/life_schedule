# --- Stylesheet tùy chỉnh (đã sửa lỗi cú pháp) ---
import os
CUSTOM_STYLESHEET = """
/* Quy tắc này sẽ ghi đè lên qdarktheme để làm nền trong suốt */
#MainContainer {
    background-color: transparent;
}
/* Quy tắc này đảm bảo nút/label điều khiển luôn tròn và có màu cam */
#ToggleButton {
    background-color: #e67e22;
    border-radius: 20px;
    border: 1px solid #d35400; /* Thêm viền nhẹ cho đẹp hơn */
}
#ToggleButton:hover {
    background-color: #f39c12;
}
/* Quy tắc này đảm bảo hộp nội dung có màu nền và bo góc như thiết kế */
#CollapsibleContainer {
    /*background-color: #34495e;*/ /* Màu nền của hộp nội dung */
    border-radius: 15px;
}
"""

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
GIF_PATH = os.path.join(WORKING_DIR, "gif", "waving_cat.gif")
print(f"Đường dẫn GIF: {GIF_PATH}")