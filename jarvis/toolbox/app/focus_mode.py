import os
import sys
import ctypes

def get_blocked_sites():
    """Đọc danh sách các trang web cần chặn từ file blocked_sites.txt."""
    blocked_sites = []
    try:
        with open("blocked_sites.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    blocked_sites.append(line)
    except FileNotFoundError:
        blocked_sites = [
            "facebook.com",
            "www.facebook.com",
            "messenger.com",
            "www.messenger.com"
        ]
    return blocked_sites

def call_hosts_manager(action, sites):
    """Gọi script hosts_manager.py với danh sách trang web cần chặn/gỡ chặn.
    returns 42 if successful, 5 if allow."""
    # Hiện UAC prompt để chạy với quyền admin
    try:
        # print(sys.executable)
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "hosts_manager.py"))
        params = f' /c {sys.executable} {script_path} {action} {" ".join(sites)}'
        print(params)
        return (ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1))
    except Exception as e:
        print(f"Lỗi khi gọi hosts_manager.py: {e}")
        return False

def activate_block():
    """Chặn các trang web trong danh sách."""
    sites = get_blocked_sites()
    return call_hosts_manager("--block", sites)

def deactivate_block():
    """Gỡ chặn tất cả các trang web."""
    sites = get_blocked_sites()
    return call_hosts_manager("--unblock", sites)

def add_blocked_site(site):
    """Thêm một trang web vào danh sách chặn."""
    sites = get_blocked_sites()
    if site not in sites:
        sites.append(site)
        with open("blocked_sites.txt", "w", encoding="utf-8") as f:
            for s in sites:
                f.write(s + "\n")

def remove_blocked_site(site):
    """Xóa một trang web khỏi danh sách chặn."""
    sites = get_blocked_sites()
    if site in sites:
        sites.remove(site)
        with open("blocked_sites.txt", "w", encoding="utf-8") as f:
            for s in sites:
                f.write(s + "\n")
