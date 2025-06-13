# app/hosts_manager.py

import sys
import platform
import tempfile
import shutil
import ctypes
import os


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() if platform.system() == "Windows" else (os.getuid() == 0)
    except Exception as e:
        import traceback
        print(f"Lỗi khi sửa file hosts: {e}")
        traceback.print_exc()


def update_hosts(action, sites):
    """Thực hiện sửa file hosts theo action và danh sách trang web."""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows" else "/etc/hosts"
    try:
        with open(hosts_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if action == "--block":
            print("Đang cập nhật file hosts để chặn các trang web...")
            # Lọc ra các dòng không chứa trang web cần chặn (tránh trùng lặp)
            new_lines = []
            is_block_section = False
            for line in lines:
                if "# --- Bắt đầu chặn" in line:
                    is_block_section = True
                elif "# --- Kết thúc chặn ---" in line:
                    is_block_section = False
                elif not is_block_section:
                    new_lines.append(line)
            # Thêm các dòng chặn mới
            new_lines.append("\n# --- Bắt đầu chặn (tự động thêm bởi FocusToolbar) ---\n")
            for site in sites:
                new_lines.append(f"127.0.0.1 {site}\n")
            new_lines.append("# --- Kết thúc chặn ---\n")
        elif action == "--unblock":
            print("Đang cập nhật file hosts để gỡ chặn các trang web...")
            # Lọc ra các dòng không chứa trang web chặn (chỉ xóa trong block section)
            new_lines = []
            is_block_section = False
            for line in lines:
                if "# --- Bắt đầu chặn" in line:
                    is_block_section = True
                elif "# --- Kết thúc chặn ---" in line:
                    is_block_section = False
                elif not is_block_section:
                    new_lines.append(line)
        else:
            print("Lệnh không hợp lệ.")
            return

        # Ghi lại file hosts (sử dụng file tạm)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
            tmp.writelines(new_lines)
        
        # Thay thế file hosts bằng file tạm (cần quyền admin/root)
        shutil.copy(tmp.name, hosts_path)
        print("Đã cập nhật file hosts thành công!")

    except PermissionError:
        print("Lỗi: Bạn cần chạy chương trình với quyền quản trị viên (Admin/Root) để sửa file hosts.")
    except Exception as e:
        import traceback
        print(f"Lỗi khi sửa file hosts: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Chương trình quản lý hosts đã được khởi chạy.")
    print("Kiểm tra quyền quản trị viên...")
    if not is_admin():
        print("Lỗi: Script phải được chạy với quyền quản trị viên (Admin/Root).")
        print("Nếu bạn đã nhấn 'Yes' ở UAC prompt nhưng vẫn thấy thông báo này, hãy thử chạy lại.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python hosts_manager.py --block|--unblock site1 site2 ...")
        sys.exit(1)
    action = sys.argv[1]
    sites = sys.argv[2:] if len(sys.argv) > 2 else []
    update_hosts(action, sites)
