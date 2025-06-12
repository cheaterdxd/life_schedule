import tkinter as tk
from tkinter import simpledialog, messagebox, PhotoImage
import time, threading
import os
import sys
import datetime
import json

# try:
#     from openpyxl import Workbook, load_workbook
# except ImportError:
#     messagebox.showerror("Lỗi thiếu thư viện", "Vui lòng cài đặt thư viện openpyxl: pip install openpyxl")
#     exit()
try:
    from playsound3 import playsound
except ImportError:
    messagebox.showerror("Lỗi thiếu thư viện", "Vui lòng cài đặt thư viện playsound3: pip install playsound3")
    exit()

# --- Cấu hình ---
DEFAULT_INTERVAL_MINUTES = 15
ACTIVITY_LOG_FILE  = "activity_log.json"
SOUND_FILE = "clockbeep.wav"
ALERT_SOUND = "alert.wav"
TODO_FILE_PREFIX = "todolist_"

# --- Danh sách Cảm xúc và Phân loại Hành vi ---
EMOTION_LABELS = ["Vui", "Rất vui", "Hạnh phúc", "Hạnh phúc Viên mãn", "Bình thường", "Giận dữ", "Sầu muộn", "Rối trí", "Hổ thẹn"]
POSITIVE_EMOTIONS = ["Vui", "Rất vui", "Hạnh phúc", "Hạnh phúc Viên mãn"]
NEGATIVE_EMOTIONS = ["Giận dữ", "Sầu muộn", "Rối trí", "Hổ thẹn"]
# Cảm xúc "Bình thường" là trung tính

BEHAVIOR_CATEGORIES = [
    "Nghiên cứu có ích",
    "Đọc có ích",
    "Viết có ích",
    "Nói/ Thuyết giảng có ích",
    "Nghiên cứu không có ích",
    "Đọc không có ích",
    "Viết không có ích",
    "Nói/ Thuyết giảng không có ích",
    "Mất tập trung vào nhiệm vụ hiện tại",
    "Buồn ngủ khi đang làm việc",
    "Chơi game" # Đảm bảo "Chơi game" có trong danh sách tổng này
    # Các label khác như "Chơi", "Nghỉ ngơi", "Giải trí" nếu không có trong 2 nhóm trên
    # và bạn không muốn theo dõi riêng thì không cần liệt kê ở đây,
    # và logic phân tích sẽ bỏ qua chúng hoặc tính vào nhóm khác nếu cần.
    # Dựa trên yêu cầu "các hoạt động tôi liệt kê ở trên là tất cả, không có trung tính" cho hành vi,
    # giả định danh sách này CHỈ gồm các label có ích và không có ích.
    # Nếu bạn có các label hành vi khác KHÔNG thuộc 2 nhóm này và muốn loại bỏ khỏi phân tích,
    # thì danh sách này có thể cần liệt kê tất cả các lựa chọn trong OptionMenu
]

PRODUCTIVE_BEHAVIORS = ["Nghiên cứu có ích", "Đọc có ích", "Viết có ích", "Nói/ Thuyết giảng có ích"]
UNPRODUCTIVE_BEHAVIORS = [
    "Nghiên cứu không có ích",
    "Đọc không có ích",
    "Viết không có ích",
    "Nói/ Thuyết giảng không có ích",
    "Mất tập trung vào nhiệm vụ hiện tại",
    "Buồn ngủ khi đang làm việc",
    "Chơi game" # Đảm bảo "Chơi game" có trong nhóm không có ích
]
# ---------------------------------------------------

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả dev và PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ReminderApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Trình Nhắc Nhở Hoạt Động & Nhiệm vụ")
        # self.root.geometry("300x180")
        self.root.resizable(False, False)

        # --- Biến trạng thái nhắc nhở hoạt động (cũ) ---
        self.reminder_interval_ms = DEFAULT_INTERVAL_MINUTES * 60 * 1000
        self.next_reminder_id = None
        self.sleep_until_time = 0
        self.countdown_id = None
        self.is_running = True

        # --- Biến trạng thái nhiệm vụ (mới) ---
        self.tasks = [] # [{'name': 'Task Name', 'time': 'HH:MM', 'completed': False, 'alarm_id': None, 'completion_time': None, 'labels': []}] # Cập nhật cấu trúc nếu lưu JSON
        self.task_window = None
        self.task_creation_win = None
        self._temp_tasks_to_add = []

        # --- Âm thanh và Icon ---
        self.sound_path = resource_path(SOUND_FILE)
        self.alert_sound_path = resource_path(ALERT_SOUND)
        # self.task_alarm_sound_path = resource_path("task_alarm.wav") # Tùy chọn

        try:
            icon_path = resource_path("icon.png")
            if os.path.exists(icon_path):
                 self.root.iconphoto(True, PhotoImage(file=icon_path))
        except Exception as e:
            print(f"Không thể tải icon: {e}")

        # --- Giao diện ---
        self.status_label = tk.Label(root_window, text="Đang chạy...", font=("Helvetica", 10), pady=5)
        self.status_label.pack(fill=tk.X, padx=10)

        self.last_check_label = tk.Label(root_window, text="Chưa có lần kiểm tra hoạt động nào.", font=("Helvetica", 9), fg="gray", pady=5)
        self.last_check_label.pack(fill=tk.X, padx=10)

        button_frame = tk.Frame(root_window)
        button_frame.pack(pady=10)

        self.sleep_button = tk.Button(button_frame,
                                       text="😴 Đi ngủ",
                                       command=self.go_to_sleep,
                                       width=10,
                                       bg="lightblue",
                                       fg="black",
                                       activebackground="dodgerblue",
                                       activeforeground="white",
                                       relief="flat")
        self.sleep_button.grid(row=0, column=0, padx=5)

        self.settings_button = tk.Button(button_frame,
                                         text="⚙️ Cài đặt",
                                         command=self.change_interval,
                                         width=10,
                                         bg="lightgray",
                                         fg="black",
                                         activebackground="gray",
                                         activeforeground="white",
                                         relief="flat")
        self.settings_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(button_frame,
                                     text="⏹️ Dừng",
                                     command=self.stop_program,
                                     width=10,
                                     bg="red",
                                     fg="white",
                                     activebackground="darkred",
                                     activeforeground="white",
                                     relief="flat")
        self.stop_button.grid(row=0, column=2, padx=5)

        self.tasks_button = tk.Button(button_frame,
                                      text="📝 Nhiệm vụ",
                                      command=self.show_task_window,
                                      width=10,
                                      bg="orange",
                                      fg="black",
                                      activebackground="darkorange",
                                      activeforeground="white",
                                      relief="flat")
        self.tasks_button.grid(row=0, column=3, padx=5)


        self.ensure_activity_log_file()

        self.initialize_tasks()

        # schedule_next_reminder được gọi ở cuối initialize_tasks()
    
    def ensure_activity_log_file(self):
        """Kiểm tra và tạo file log hoạt động JSON nếu chưa có."""
        log_path = resource_path(ACTIVITY_LOG_FILE)
        # Nếu file chưa tồn tại, tạo file JSON rỗng với cấu trúc danh sách
        if not os.path.exists(log_path):
            try:
                # Ghi một danh sách rỗng [] vào file JSON
                with open(log_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"Đã tạo file log hoạt động: {log_path}")
            except Exception as e:
                messagebox.showerror("Lỗi File Log", f"Không thể tạo file {ACTIVITY_LOG_FILE}:\n{e}", parent=self.root)
                self.stop_program() # Dừng nếu không tạo được file log

    # Sửa đổi phương thức save_log để nhận thêm tham số cảm xúc và phân loại
    def save_log(self, answer, emotion, category):
        """Đọc log hoạt động hiện tại từ file JSON, thêm bản ghi mới, và lưu lại toàn bộ file."""
        log_path = resource_path(ACTIVITY_LOG_FILE)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Bản ghi hoạt động mới dưới dạng dictionary
        new_entry = {
            "timestamp": timestamp,
            "activity": answer,
            "emotion": emotion,
            "category": category
        }

        # --- Đọc dữ liệu log hiện có từ file JSON ---
        log_data = []
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    # Kiểm tra file không rỗng trước khi load
                    content = f.read()
                    if content:
                         # Giải mã nội dung JSON thành danh sách Python
                         log_data = json.loads(content)
                    else:
                         log_data = [] # File tồn tại nhưng rỗng

            except json.JSONDecodeError as e:
                 # Xử lý lỗi nếu file JSON bị hỏng
                 print(f"Lỗi giải mã JSON file log hoạt động {log_path}: {e}")
                 messagebox.showwarning("Lỗi Đọc Log", f"Không thể đọc file log hoạt động (lỗi JSON):\n{e}\n\nTiến hành ghi bản ghi mới vào file trống hoặc ghi đè.", parent=self.root)
                 log_data = [] # Bỏ qua dữ liệu lỗi, bắt đầu với danh sách rỗng

            except Exception as e:
                # Xử lý các lỗi đọc file khác
                print(f"Lỗi khi đọc file log hoạt động {log_path}:\n{e}")
                messagebox.showwarning("Lỗi Đọc Log", f"Không thể đọc file log hoạt động:\n{e}\n\nTiến hành ghi bản ghi mới vào file trống hoặc ghi đè.", parent=self.root)
                log_data = [] # Bỏ qua dữ liệu lỗi


        # --- Thêm bản ghi mới vào danh sách dữ liệu đã đọc ---
        log_data.append(new_entry)

        # --- Ghi lại toàn bộ danh sách log đã cập nhật vào file JSON ---
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                 # use ensure_ascii=False để hỗ trợ tiếng Việt
                 # use indent=4 để file JSON được định dạng đẹp, dễ đọc hơn khi mở bằng trình soạn thảo văn bản
                 json.dump(log_data, f, ensure_ascii=False, indent=4)

            print(f"Đã lưu bản ghi hoạt động mới vào file log: {log_path}")
            # Cập nhật Label thời gian kiểm tra cuối (giữ nguyên)
            self.last_check_label.config(text=f"Lần cuối kiểm tra hoạt động lúc: {timestamp}", fg="black")

        except Exception as e:
            # Xử lý lỗi ghi file
            print(f"Lỗi khi ghi file log hoạt động {log_path}:\n{e}")
            messagebox.showwarning("Lỗi Ghi Log", f"Không thể ghi file log hoạt động:\n{e}\n\nBản ghi có thể không được lưu.", parent=self.root)


    def play_notification_sound(self):
        """Phát âm thanh thông báo nhắc nhở hoạt động."""
        try:
            threading.Thread(target=playsound, args=(self.sound_path,), daemon=True).start()
        except Exception as e:
            print(f"Lỗi khi phát âm thanh nhắc nhở '{self.sound_path}': {e}")

    def schedule_next_reminder(self):
        """Lên lịch cho lần nhắc nhở hoạt động tiếp theo."""
        if self.next_reminder_id:
            self.root.after_cancel(self.next_reminder_id)
            self.next_reminder_id = None

        if self.is_running and time.time() >= self.sleep_until_time:
            print(f"Lên lịch nhắc nhở hoạt động sau {self.reminder_interval_ms // 1000} giây.")
            delay_ms = self.reminder_interval_ms
            self.next_reminder_id = self.root.after(delay_ms, self.ask_question)
            if self.countdown_id is None:
                 self.status_label.config(text=f"Đang chạy... Nhắc nhở sau {delay_ms // 60000} phút")
        elif self.is_running and time.time() < self.sleep_until_time:
             wake_up_delay = int((self.sleep_until_time - time.time()) * 1000)
             if wake_up_delay < 0:
                 wake_up_delay = 0
             print(f"Đang ngủ, kiểm tra lại sau {wake_up_delay / 1000:.0f} giây.")
             self.next_reminder_id = self.root.after(wake_up_delay + 500, self.schedule_next_reminder)

    # Sửa đổi phương thức ask_question để thêm chọn cảm xúc và phân loại
    def ask_question(self):
        """Hỏi người dùng về hoạt động, cảm xúc, phân loại, yêu cầu nhập, và hiển thị indicator hiệu suất."""
        if not self.is_running or time.time() < self.sleep_until_time:
            print("Bỏ qua cửa sổ hỏi do đang dừng hoặc ngủ.")
            if self.is_running and time.time() < self.sleep_until_time:
                 self.schedule_next_reminder()
            return

        self.play_notification_sound()

        ask_win = tk.Toplevel(self.root)
        ask_win.title("Nhập Hoạt động & Trạng thái")
        ask_win.resizable(False, False)

        try:
            ask_win.attributes("-fullscreen", True)
        except tk.TclError:
            print("Cảnh báo: Chế độ toàn màn hình Tkinter có thể không được hỗ trợ đầy đủ. Thử phóng to tối đa.")
            ask_win.state('zoomed')
            ask_win.attributes("-topmost", True)

        ask_win.attributes("-topmost", True)
        ask_win.grab_set()

        content_frame = tk.Frame(ask_win)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # --- Hiển thị các Indicator Hiệu suất (MỚI) ---
        performance_indicators = self.get_performance_indicators()

        # Frame để chứa các icon và thông báo hiệu suất
        indicator_frame = tk.Frame(content_frame)
        indicator_frame.pack(pady=(0, 20)) # Đặt ở trên cùng, cách nội dung bên dưới 20px

        # Label cho Icon chính (Quy tắc 1)
        main_icon_label = tk.Label(indicator_frame, text=performance_indicators['main_status_icon'], font=("Helvetica", 24)) # Icon to hơn
        main_icon_label.pack(side=tk.LEFT, padx=10) # Đặt bên trái

        # Label cho thông báo chính (Quy tắc 1)
        main_message_label = tk.Label(indicator_frame, text=performance_indicators['main_status_message'], font=("Helvetica", 14))
        main_message_label.pack(side=tk.LEFT, padx=10) # Đặt ở giữa

        # Label cho Icon xu hướng (Quy tắc 2)
        trend_icon_label = tk.Label(indicator_frame, text=performance_indicators['trend_icon'], font=("Helvetica", 24)) # Icon to hơn
        trend_icon_label.pack(side=tk.LEFT, padx=10) # Đặt bên phải

        # --- Kết thúc hiển thị Indicator ---


        # --- Phần nhập Hoạt động ---
        label_activity = tk.Label(content_frame, text=f"Bạn đã làm gì trong {self.reminder_interval_ms // (60 * 1000)} phút vừa qua?", font=("Helvetica", 16, "bold"))
        label_activity.pack(pady=(0, 10)) # Điều chỉnh pady sau indicator frame

        entry_activity = tk.Entry(content_frame, width=60, font=("Helvetica", 14))
        entry_activity.pack(pady=(0, 15))
        entry_activity.focus_set()

        # --- Phần chọn Cảm xúc ---
        label_emotion = tk.Label(content_frame, text="Cảm xúc của bạn lúc đó là gì?", font=("Helvetica", 14))
        label_emotion.pack(pady=(10, 0))

        selected_emotion = tk.StringVar(content_frame)
        if EMOTION_LABELS:
            selected_emotion.set(EMOTION_LABELS[0])
        else:
            selected_emotion.set("Không có lựa chọn")

        if EMOTION_LABELS:
            emotion_menu = tk.OptionMenu(content_frame, selected_emotion, *EMOTION_LABELS)
        else:
            emotion_menu = tk.OptionMenu(content_frame, selected_emotion, selected_emotion.get())

        emotion_menu.config(font=("Helvetica", 12), width=30)
        emotion_menu.pack(pady=(0, 15))

        # --- Phần chọn Phân loại hành vi ---
        label_category = tk.Label(content_frame, text="Phân loại hành vi này là gì?", font=("Helvetica", 14))
        label_category.pack(pady=(10, 0))

        selected_category = tk.StringVar(content_frame)
        if BEHAVIOR_CATEGORIES:
            selected_category.set(BEHAVIOR_CATEGORIES[0])
        else:
            selected_category.set("Không có lựa chọn")

        if BEHAVIOR_CATEGORIES:
            category_menu = tk.OptionMenu(content_frame, selected_category, *BEHAVIOR_CATEGORIES)
        else:
            category_menu = tk.OptionMenu(content_frame, selected_category, selected_category.get())

        category_menu.config(font=("Helvetica", 12), width=30)
        category_menu.pack(pady=(0, 20))

        # --- Hàm xử lý khi nhấn nút Xác nhận hoặc Enter ---
        def submit_answer():
            answer = entry_activity.get().strip()
            emotion = selected_emotion.get()
            category = selected_category.get()

            if not answer:
                messagebox.showwarning("Thông tin cần thiết", "Vui lòng nhập hoạt động của bạn trước khi xác nhận.", parent=ask_win)
                entry_activity.focus_set()
                return

            self.save_log(answer, emotion, category)
            ask_win.destroy()
            self.schedule_next_reminder()

        # Nút Xác nhận
        submit_button = tk.Button(content_frame, text="Xác nhận", command=submit_answer, width=15, font=("Helvetica", 14))
        submit_button.pack(pady=10)

        entry_activity.bind("<Return>", lambda event: submit_answer())

        def prevent_closing():
             messagebox.showwarning("Không thể đóng", "Bạn cần nhập hoạt động của mình và nhấn 'Xác nhận' hoặc Enter.", parent=ask_win)
             entry_activity.focus_set()

        ask_win.protocol("WM_DELETE_WINDOW", prevent_closing)

    def go_to_sleep(self):
        """Tạm dừng nhắc nhở hoạt động trong một khoảng thời gian."""
        if self.countdown_id:
             messagebox.showinfo("Thông báo", "Đang trong chế độ ngủ rồi.", parent=self.root)
             return

        minutes = simpledialog.askinteger("Đi ngủ", "Bạn muốn nghỉ trong bao nhiêu phút?",
                                          minvalue=1, maxvalue=1440, parent=self.root)
        if minutes is not None:
            if self.next_reminder_id:
                self.root.after_cancel(self.next_reminder_id)
                self.next_reminder_id = None
                print("Đã hủy lịch nhắc nhở hoạt động do đi ngủ.")

            self.sleep_until_time = time.time() + minutes * 60
            messagebox.showinfo("Thông báo", f"Sẽ không nhắc nhở hoạt động trong {minutes} phút tới.", parent=self.root)
            self.update_countdown()


    def update_countdown(self):
        """Cập nhật hiển thị đếm ngược thời gian ngủ trên status_label."""
        if self.countdown_id:
            self.root.after_cancel(self.countdown_id)
            self.countdown_id = None

        remaining = int(self.sleep_until_time - time.time())

        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            self.status_label.config(text=f"😴 Đang ngủ: còn {mins:02d}:{secs:02d}")
            self.countdown_id = self.root.after(1000, self.update_countdown)
        else:
            self.status_label.config(text="Đã thức dậy!")
            self.sleep_until_time = 0
            self.countdown_id = None
            print("Hết giờ ngủ.")
            self.schedule_next_reminder()


    def change_interval(self):
        """Thay đổi khoảng thời gian giữa các lần nhắc nhở hoạt động."""
        current_interval_min = self.reminder_interval_ms // (60 * 1000)
        new_minutes = simpledialog.askinteger("Cài đặt thời gian",
                                              f"Nhập khoảng thời gian nhắc nhở hoạt động (phút):\n(Hiện tại: {current_interval_min} phút)",
                                              minvalue=1, maxvalue=120, parent=self.root,
                                              initialvalue=current_interval_min)
        if new_minutes is not None and new_minutes != current_interval_min:
            self.reminder_interval_ms = new_minutes * 60 * 1000
            messagebox.showinfo("Thông báo", f"Đã cập nhật khoảng thời gian nhắc nhở hoạt động thành {new_minutes} phút.", parent=self.root)
            print(f"Đã đổi khoảng thời gian nhắc nhở hoạt động thành {new_minutes} phút.")
            if time.time() >= self.sleep_until_time:
                 self.schedule_next_reminder()

    # --- Phương thức liên quan đến Nhiệm vụ ---
    # initialize_tasks, get_today_todo_filepath, check_and_load_todolist, save_todolist,
    # play_alert_sound, show_task_window, show_task_creation_window,
    # add_task_from_entries, save_and_close_task_creation,
    # schedule_task_alarms, trigger_task_alarm, cancel_task_alarm, cancel_all_task_alarms
    # Các phương thức này giữ nguyên như trong mã trước đó
    # (có thể cần điều chỉnh lại show_task_window và các hàm quản lý nhiệm vụ sau khi chuyển sang JSON)

    def initialize_tasks(self):
        """Kiểm tra file todolist của hôm nay, tải nhiệm vụ nếu có và lên lịch báo thức."""
        print("Đang kiểm tra và tải nhiệm vụ...")
        # --- Lưu ý: check_and_load_todolist hiện tại chỉ đọc TXT, cần chuyển sang JSON ---
        tasks_exist = self.check_and_load_todolist()

        if not tasks_exist or not self.tasks:
            print("Không tìm thấy file nhiệm vụ hoặc file trống. Phát cảnh báo và yêu cầu tạo.")
            self.play_alert_sound()
            messagebox.showinfo("Thông báo Nhiệm vụ",
                                f"Không tìm thấy file nhiệm vụ cho hôm nay ({datetime.date.today().strftime('%d/%m/%Y')}). Vui lòng tạo nhiệm vụ mới.",
                                parent=self.root)
        else:
             print("Đã tải nhiệm vụ. Đang lên lịch báo thức...")
             # --- Lưu ý: schedule_task_alarms dựa trên cấu trúc task hiện tại (chưa có completion_time, labels) ---
             self.schedule_task_alarms()

        self.schedule_next_reminder()

    def get_today_todo_filepath(self):
        """Trả về đường dẫn đầy đủ đến file nhiệm vụ của ngày hôm nay (YYYYMMDD.json)."""
        today_str = datetime.date.today().strftime("%Y%m%d")
        # --- Đổi đuôi file nhiệm vụ sang .json ---
        filename = f"{TODO_FILE_PREFIX}{today_str}.json"
        # --------------------------------------
        return resource_path(filename)
    
    def check_and_load_todolist(self):
        """Kiểm tra file nhiệm vụ JSON của hôm nay, tải nội dung nếu có.
           Trả về True nếu file tồn tại và không có lỗi đọc, False nếu không tồn tại hoặc lỗi."""
        filepath = self.get_today_todo_filepath() # Sử dụng đường dẫn file .json
        self.tasks = [] # Xóa danh sách nhiệm vụ hiện tại trước khi tải

        if os.path.exists(filepath):
            print(f"Tìm thấy file nhiệm vụ: {filepath}")
            try:
                # --- Đọc file JSON ---
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Kiểm tra file không rỗng trước khi load
                    content = f.read()
                    if content:
                         # Parse nội dung JSON thành danh sách các dictionary Python
                         self.tasks = json.loads(content)
                    else:
                         self.tasks = [] # File rỗng, danh sách nhiệm vụ trống

                # --- Xử lý tương thích ngược và thêm các khóa mặc định nếu file cũ thiếu ---
                # Điều này giúp ứng dụng hoạt động với file JSON cũ hơn (nếu có)
                for task in self.tasks:
                    # alarm_id không được lưu trong file, cần khởi tạo lại mỗi lần tải
                    task['alarm_id'] = None
                    # Thêm các khóa mới nếu file JSON cũ không có chúng (đảm bảo cấu trúc đồng nhất)
                    if 'completed' not in task:
                        task['completed'] = False # Mặc định là False nếu không có
                    if 'completion_time' not in task:
                         task['completion_time'] = None # Mặc định là None nếu không có
                    if 'labels' not in task:
                         task['labels'] = [] # Mặc định là danh sách rỗng nếu không có
                    if 'scheduled_time' not in task:
                         # Mặc định scheduled_time lấy từ 'time' nếu không có khóa scheduled_time
                         task['scheduled_time'] = task.get('time')
                    # Đảm bảo có ít nhất khóa 'name' và 'time' để nhiệm vụ hợp lệ
                    if 'name' not in task or 'time' not in task:
                         print(f"Cảnh báo: Nhiệm vụ có cấu trúc không đầy đủ bị bỏ qua khi tải: {task}")
                         # Sử dụng list slicing hoặc list comprehension để xóa an toàn khi lặp
                         continue # Bỏ qua nhiệm vụ không hợp lệ trong vòng lặp for

                # Sau vòng lặp, lọc lại danh sách self.tasks để bỏ các nhiệm vụ không hợp lệ
                self.tasks = [task for task in self.tasks if 'name' in task and 'time' in task]


                print(f"Đã tải {len(self.tasks)} nhiệm vụ từ file JSON.")
                return True
            except json.JSONDecodeError as e:
                 print(f"Lỗi giải mã JSON file nhiệm vụ {filepath}: {e}")
                 messagebox.showerror("Lỗi File Nhiệm vụ", f"Không thể đọc file nhiệm vụ {filepath} (lỗi JSON):\n{e}", parent=self.root)
                 # Tùy chọn: Đổi tên file bị lỗi để không đọc lại lần sau và cho người dùng kiểm tra
                 # os.rename(filepath, filepath + ".backup." + time.strftime("%Y%m%d%H%M%S"))
                 return False
            except Exception as e:
                print(f"Lỗi khi đọc file nhiệm vụ {filepath}:\n{e}")
                messagebox.showerror("Lỗi File Nhiệm vụ", f"Không thể đọc file nhiệm vụ {filepath}:\n{e}", parent=self.root)
                return False
        else:
            print(f"Không tìm thấy file nhiệm vụ: {filepath}")
            return False # File không tồn tại

    def save_todolist(self):
        """Lưu danh sách nhiệm vụ hiện tại (từ self.tasks) vào file JSON của ngày hôm nay."""
        
        filepath = self.get_today_todo_filepath() # Sử dụng đường dẫn file .json

        # Chuẩn bị dữ liệu để lưu: loại bỏ các khóa không cần thiết (như alarm_id)
        tasks_to_save = []
        for task in self.tasks:
            task_copy = task.copy() # Tạo bản sao để không ảnh hưởng đến dictionary gốc
            # Kiểm tra sự tồn tại của khóa 'alarm_id' trước khi cố gắng xóa
            if 'alarm_id' in task_copy:
                del task_copy['alarm_id'] # ID báo thức chỉ tồn tại khi ứng dụng chạy, không lưu vào file

            # Thêm bản sao đã loại bỏ 'alarm_id' vào danh sách sẽ ghi ra file
            tasks_to_save.append(task_copy)

        try:
            # --- Ghi file JSON ---
            # use ensure_ascii=False để Python ghi ký tự tiếng Việt mà không mã hóa (ví dụ: \u1ef9)
            # use indent=4 để file JSON được định dạng đẹp, dễ đọc hơn khi mở bằng trình soạn thảo văn bản
            with open(filepath, 'w', encoding='utf-8') as f:
                 json.dump(tasks_to_save, f, ensure_ascii=False, indent=4)
            print(f"Đã lưu {len(tasks_to_save)} nhiệm vụ vào file JSON: {filepath}")
        except Exception as e:
            print(f"Lỗi khi ghi file nhiệm vụ {filepath}: {e}")
            messagebox.showerror("Lỗi Lưu Nhiệm vụ", f"Không thể ghi file nhiệm vụ {filepath}:\n{e}", parent=self.root)
    
    def play_alert_sound(self):
        """Phát âm thanh cảnh báo (khi không tìm thấy file nhiệm vụ)."""
        try:
            if os.path.exists(self.alert_sound_path):
                threading.Thread(target=playsound, args=(self.alert_sound_path,), daemon=True).start()
            else:
                print(f"Không tìm thấy file âm thanh cảnh báo: {self.alert_sound_path}")
        except Exception as e:
            print(f"Lỗi khi phát âm thanh cảnh báo '{self.alert_sound_path}': {e}")

    def show_task_window(self):
        """Hiển thị cửa sổ quản lý/xem nhiệm vụ của hôm nay."""
        if self.task_window is None or not self.task_window.winfo_exists():
            self.task_window = tk.Toplevel(self.root)
            self.task_window.title(f"Nhiệm vụ hôm nay ({datetime.date.today().strftime('%d/%m/%Y')})")
            self.task_window.transient(self.root)
            self.task_window.grab_set()

            label = tk.Label(self.task_window, text="Danh sách nhiệm vụ của bạn:")
            label.pack(pady=5)

            add_button = tk.Button(self.task_window, text="➕ Thêm Nhiệm vụ mới", command=self.show_task_creation_window)
            add_button.pack(pady=5)

            # --- Cần triển khai hiển thị danh sách nhiệm vụ JSON ở đây ---
            self.display_tasks_in_window() # Hàm mới để hiển thị chi tiết
            # ------------------------------------------------------------

            close_button = tk.Button(self.task_window, text="Đóng", command=self.task_window.destroy)
            close_button.pack(pady=10)

            self.task_window.protocol("WM_DELETE_WINDOW", self.task_window.destroy)


        self.task_window.lift()

    # --- Phương thức mới để hiển thị nhiệm vụ trong cửa sổ xem ---
    def display_tasks_in_window(self):
        """Hiển thị chi tiết các nhiệm vụ trong cửa sổ task_window."""
        # Xóa nội dung hiển thị cũ nếu có
        for widget in self.task_window.winfo_children():
            if getattr(widget, '_is_task_display', False): # Đánh dấu các widget hiển thị nhiệm vụ
                widget.destroy()

        if not self.tasks:
             no_tasks_label = tk.Label(self.task_window, text="Chưa có nhiệm vụ nào được thêm cho hôm nay.", fg="gray")
             no_tasks_label.pack(pady=10)
             setattr(no_tasks_label, '_is_task_display', True) # Đánh dấu để xóa sau
        else:
             # --- HIỂN THỊ DANH SÁCH NHIỆM VỤ (CẦN TRIỂN KHAI THÊM) ---
             # Tạo Frame hoặc Canvas có Scrollbar nếu danh sách dài
             task_display_frame = tk.Frame(self.task_window)
             task_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
             setattr(task_display_frame, '_is_task_display', True) # Đánh dấu để xóa

             # Cần vòng lặp để tạo widget (Label, Checkbutton/Button) cho từng nhiệm vụ
             for i, task in enumerate(self.tasks):
                 task_frame = tk.Frame(task_display_frame) # Frame cho mỗi nhiệm vụ
                 task_frame.pack(fill=tk.X, pady=2)

                 # --- Hiển thị thông tin nhiệm vụ ---
                 # Cần xử lý hiển thị trạng thái hoàn thành và nhãn
                 status_char = "✅" if task.get('completed', False) else "⬜" # Lấy trạng thái, mặc định là False
                 task_text = f"{status_char} {task.get('time', 'N/A')} - {task.get('name', 'Không tên')}"
                 labels_text = ", ".join(task.get('labels', [])) # Lấy danh sách nhãn
                 if labels_text:
                      task_text += f" [{labels_text}]"

                 task_label = tk.Label(task_frame, text=task_text, anchor='w')
                 # Áp dụng style nếu đã hoàn thành
                 if task.get('completed', False):
                     task_label.config(fg="gray", font=("Helvetica", 10, "overstrike")) # Gạch ngang và màu xám


                 task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

                 # --- Thêm nút hoặc Checkbutton để đánh dấu hoàn thành (CẦN TRIỂN KHAI LOGIC) ---
                 if not task.get('completed', False): # Chỉ hiển thị nút hoàn thành nếu chưa xong
                     complete_button = tk.Button(task_frame, text="Hoàn thành", command=lambda t=task: self.mark_task_completed(t)) # Cần viết hàm mark_task_completed
                     complete_button.pack(side=tk.RIGHT)


             # --- KẾT THÚC HIỂN THỊ DANH SÁCH NHIỆM VỤ ---


    def show_task_creation_window(self):
        """Hiển thị cửa sổ cho phép người dùng nhập nhiệm vụ mới."""
        if self.task_creation_win is None or not self.task_creation_win.winfo_exists():
            self.task_creation_win = tk.Toplevel(self.root)
            self.task_creation_win.title("Tạo Nhiệm vụ mới")
            self.task_creation_win.geometry("400x350") # Tăng kích thước để chứa label
            self.task_creation_win.transient(self.root)
            self.task_creation_win.grab_set()

            self._temp_tasks_to_add = []

            tk.Label(self.task_creation_win, text="Tên Nhiệm vụ:").pack(pady=(10,0))
            task_name_entry = tk.Entry(self.task_creation_win, width=40)
            task_name_entry.pack(pady=(0,5))
            task_name_entry.focus_set()

            tk.Label(self.task_creation_win, text="Thời gian (HH:MM - 24h):").pack(pady=(10,0))
            task_time_entry = tk.Entry(self.task_creation_win, width=10)
            task_time_entry.pack(pady=(0,5))

            # --- Phần nhập Nhãn/Phân loại Nhiệm vụ (MỚI) ---
            tk.Label(self.task_creation_win, text="Nhãn/Phân loại (phân cách bởi dấu phẩy):").pack(pady=(10,0))
            task_labels_entry = tk.Entry(self.task_creation_win, width=40)
            task_labels_entry.pack(pady=(0,5))
            # -----------------------------------------------


            button_frame = tk.Frame(self.task_creation_win)
            button_frame.pack(pady=10)

            add_button = tk.Button(button_frame, text="➕ Thêm vào danh sách tạm",
                                   command=lambda: self.add_task_from_entries(task_name_entry, task_time_entry, task_labels_entry)) # Truyền thêm entry nhãn
            add_button.grid(row=0, column=0, padx=5)

            save_button = tk.Button(button_frame, text="💾 Lưu tất cả và Đóng",
                                    command=self.save_and_close_task_creation)
            save_button.grid(row=0, column=1, padx=5)

            cancel_button = tk.Button(button_frame, text="❌ Hủy",
                                      command=self.task_creation_win.destroy)
            cancel_button.grid(row=0, column=2, padx=5)

            self.task_creation_win.protocol("WM_DELETE_WINDOW", self.task_creation_win.destroy)


        self.task_creation_win.lift()


    # Sửa đổi phương thức add_task_from_entries để lấy và xử lý nhãn
    def add_task_from_entries(self, task_name_entry, task_time_entry, task_labels_entry): # Thêm tham số entry nhãn
        """Lấy dữ liệu từ Entry trong cửa sổ tạo nhiệm vụ, validate và thêm vào danh sách tạm thời."""
        name = task_name_entry.get().strip()
        time_str = task_time_entry.get().strip()
        labels_str = task_labels_entry.get().strip() # Lấy chuỗi nhãn

        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên nhiệm vụ.", parent=self.task_creation_win)
            return
        if not time_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập thời gian nhiệm vụ (HH:MM).", parent=self.task_creation_win)
            return

        # Xác thực định dạng thời gian cơ bản (HH:MM)
        try:
            hours, minutes = map(int, time_str.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                 raise ValueError("Giờ hoặc phút không hợp lệ")
            datetime.datetime.strptime(time_str, "%H:%M") # Kiểm tra định dạng
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Thời gian không hợp lệ. Vui lòng nhập theo định dạng HH:MM (ví dụ: 09:00, 14:30).", parent=self.task_creation_win)
            return

        # Xử lý chuỗi nhãn thành danh sách
        labels = [label.strip() for label in labels_str.split(',') if label.strip()] # Tách bằng dấu phẩy, loại bỏ khoảng trắng và mục rỗng

        # Thêm nhiệm vụ vào danh sách tạm thời với các khóa mới
        self._temp_tasks_to_add.append({
            'name': name,
            'time': time_str, # Thời gian dự kiến HH:MM
            'scheduled_time': time_str, # Thời gian thực tế lên lịch (có thể khác time nếu cần điều chỉnh) - Lưu vào file
            'completed': False, # Ban đầu là chưa hoàn thành
            'completion_time': None, # Ban đầu chưa có thời gian hoàn thành
            'labels': labels, # Danh sách các nhãn
            'alarm_id': None # ID báo thức (chỉ dùng runtime)
        })
        print(f"Đã thêm tạm nhiệm vụ: {name} lúc {time_str} với nhãn {labels}")

        messagebox.showinfo("Thành công", f"Đã thêm tạm nhiệm vụ '{name}' vào danh sách chờ lưu.", parent=self.task_creation_win)
        task_name_entry.delete(0, tk.END)
        task_time_entry.delete(0, tk.END)
        task_labels_entry.delete(0, tk.END) # Xóa ô nhãn
        task_name_entry.focus_set()

    def save_and_close_task_creation(self):
        """Lưu tất cả các nhiệm vụ từ danh sách tạm thời vào danh sách chính và file, sau đó đóng cửa sổ tạo."""
        if not self._temp_tasks_to_add:
            messagebox.showinfo("Thông báo", "Chưa có nhiệm vụ mới nào được thêm để lưu.", parent=self.task_creation_win)
            self.task_creation_win.destroy()
            return

        self.tasks.extend(self._temp_tasks_to_add)
        self._temp_tasks_to_add = []

        # --- Lưu danh sách nhiệm vụ chính vào file JSON ---
        self.save_todolist()

        # --- Hủy báo thức cũ và lên lịch lại cho TẤT CẢ nhiệm vụ ---
        self.cancel_all_task_alarms()
        self.schedule_task_alarms()

        # --- Cập nhật hiển thị trong cửa sổ xem nhiệm vụ nếu nó đang mở ---
        if self.task_window and self.task_window.winfo_exists():
             self.display_tasks_in_window() # Gọi hàm hiển thị để làm mới


        messagebox.showinfo("Lưu thành công", f"Đã lưu tổng cộng {len(self.tasks)} nhiệm vụ vào file.", parent=self.task_creation_win)
        self.task_creation_win.destroy()

    # --- Phương thức cần viết để xử lý đánh dấu hoàn thành (MỚI) ---
    def mark_task_completed(self, task_to_complete):
        """Đánh dấu một nhiệm vụ là đã hoàn thành và ghi lại thời gian."""
        for task in self.tasks:
            # Tìm đúng nhiệm vụ trong danh sách
            # Cần một cách nhận dạng nhiệm vụ duy nhất nếu có nhiều nhiệm vụ cùng tên/thời gian
            # Tạm thời so sánh cả tên và thời gian
            if task['name'] == task_to_complete['name'] and task['time'] == task_to_complete['time'] and not task['completed']:
                task['completed'] = True
                task['completion_time'] = time.strftime("%Y-%m-%d %H:%M:%S") # Ghi lại thời gian hoàn thành
                self.cancel_task_alarm(task) # Hủy báo thức nếu có
                self.save_todolist() # Lưu lại thay đổi vào file
                print(f"Đã đánh dấu hoàn thành nhiệm vụ: {task['name']} lúc {task['completion_time']}")

                # Cập nhật hiển thị trong cửa sổ xem nhiệm vụ
                if self.task_window and self.task_window.winfo_exists():
                     self.display_tasks_in_window() # Làm mới hiển thị

                messagebox.showinfo("Hoàn thành Nhiệm vụ", f"Chúc mừng! Bạn đã hoàn thành nhiệm vụ:\n'{task['name']}'", parent=self.root)
                return # Thoát sau khi tìm thấy và xử lý


    def schedule_task_alarms(self):
        """Lên lịch báo thức cho tất cả các nhiệm vụ chưa hoàn thành trong self.tasks."""
        now = datetime.datetime.now()
        today = now.date()
        print(f"Đang lên lịch báo thức nhiệm vụ từ {len(self.tasks)} nhiệm vụ...")

        for task in self.tasks:
            # Chỉ lên lịch cho nhiệm vụ chưa hoàn thành và chưa có báo thức
            if not task.get('completed', False) and task.get('alarm_id') is None:
                try:
                    # Lấy thời gian lên lịch từ khóa 'scheduled_time' hoặc 'time' nếu không có
                    task_time_str = task.get('scheduled_time', task.get('time'))
                    if not task_time_str:
                         print(f"Nhiệm vụ '{task.get('name', 'Không tên')}' thiếu thời gian. Bỏ qua lên lịch.")
                         continue

                    task_hour, task_minute = map(int, task_time_str.split(':'))
                    task_datetime = datetime.datetime.combine(today, datetime.time(task_hour, task_minute))

                    # Nếu thời gian nhiệm vụ đã trôi qua trong ngày hôm nay, không lên lịch
                    if task_datetime <= now:
                        print(f"Bỏ qua lên lịch cho nhiệm vụ '{task.get('name', 'Không tên')}' lúc {task_time_str} vì đã trôi qua.")
                        continue

                    time_difference = task_datetime - now
                    delay_ms = int(time_difference.total_seconds() * 1000)

                    if delay_ms > 0:
                        task['alarm_id'] = self.root.after(delay_ms, lambda t=task: self.trigger_task_alarm(t))
                        print(f"Đã lên lịch báo thức cho '{task.get('name', 'Không tên')}' lúc {task_time_str} (sau {delay_ms / 1000:.0f}s).")
                    else:
                         print(f"Thời gian cho nhiệm vụ '{task.get('name', 'Không tên')}' lúc {task_time_str} quá gần hoặc đã trôi qua. Bỏ qua lên lịch.")

                except ValueError:
                    print(f"Lỗi định dạng thời gian cho nhiệm vụ '{task.get('name', 'Không tên')}': {task_time_str}. Bỏ qua lên lịch.")
                except Exception as e:
                    print(f"Lỗi khi lên lịch báo thức cho '{task.get('name', 'Không tên')}': {e}")


    def trigger_task_alarm(self, task):
        """Kích hoạt báo thức cho một nhiệm vụ cụ thể."""
        print(f"Đã đến giờ nhiệm vụ: {task.get('name', 'Không tên')}")

        self.play_notification_sound()

        messagebox.showinfo("⏰ Báo thức Nhiệm vụ", f"Đã đến giờ thực hiện nhiệm vụ:\n\n{task.get('name', 'Không tên')}", parent=self.root)

        task['alarm_id'] = None # Đặt lại ID sau khi báo thức kêu

        # Cập nhật hiển thị trong cửa sổ xem nhiệm vụ
        if self.task_window and self.task_window.winfo_exists():
             self.display_tasks_in_window()


    def cancel_task_alarm(self, task):
        """Hủy báo thức cho một nhiệm vụ cụ thể nếu nó đang chờ."""
        if task.get('alarm_id') is not None:
            try:
                self.root.after_cancel(task['alarm_id'])
                print(f"Đã hủy báo thức cho nhiệm vụ '{task.get('name', 'Không tên')}'.")
            except Exception as e:
                print(f"Lỗi khi hủy báo thức '{task.get('name', 'Không tên')}' (ID: {task['alarm_id']}): {e}")
            task['alarm_id'] = None # Luôn đặt ID về None sau khi hủy hoặc thử hủy

    def cancel_all_task_alarms(self):
        """Hủy tất cả báo thức nhiệm vụ đang chờ."""
        print("Đang hủy tất cả báo thức nhiệm vụ...")
        for task in self.tasks:
            self.cancel_task_alarm(task)
        print("Đã hủy tất cả báo thức nhiệm vụ.")

    def stop_program(self):
        """Dừng ứng dụng hoàn toàn."""
        print("Yêu cầu dừng ứng dụng.")
        self.is_running = False

        if self.next_reminder_id:
            self.root.after_cancel(self.next_reminder_id)
            self.next_reminder_id = None
            print("Đã hủy lịch nhắc nhở hoạt động cuối cùng.")
        if self.countdown_id:
            self.root.after_cancel(self.countdown_id)
            self.countdown_id = None
            print("Đã hủy lịch đếm ngược.")

        self.cancel_all_task_alarms()

        print("Dừng ứng dụng.")
        self.root.destroy()

    def get_recent_activity_logs(self, timeframe_days):
        """
        Đọc log hoạt động từ file JSON và lọc các bản ghi trong khoảng thời gian 'timeframe_days' gần nhất.
        Trả về danh sách các bản ghi log (dictionary).
        """
        log_path = resource_path(ACTIVITY_LOG_FILE)
        recent_logs = []
        now = datetime.datetime.now()
        # Tính thời điểm bắt đầu cần lọc
        start_time = now - datetime.timedelta(days=timeframe_days)

        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        log_data = json.loads(content)
                    else:
                        log_data = [] # File rỗng

                # Lọc các bản ghi theo thời gian
                for entry in log_data:
                    try:
                        # Chuyển chuỗi timestamp trong log thành đối tượng datetime
                        entry_time = datetime.datetime.strptime(entry.get("timestamp"), "%Y-%m-%d %H:%M:%S")
                        # Kiểm tra xem bản ghi có nằm trong khoảng thời gian gần nhất không
                        if entry_time >= start_time and entry_time <= now:
                            recent_logs.append(entry)
                    except (ValueError, TypeError):
                        # Bỏ qua các bản ghi có định dạng timestamp lỗi hoặc thiếu
                        print(f"Cảnh báo: Bỏ qua bản ghi log có định dạng thời gian lỗi: {entry.get('timestamp')}")
                        continue

            except json.JSONDecodeError as e:
                print(f"Lỗi giải mã JSON file log hoạt động {log_path} khi đọc dữ liệu gần đây: {e}")
                # messagebox.showwarning("Lỗi Đọc Log", f"Không thể đọc file log hoạt động để phân tích:\n{e}", parent=self.root)
                return [] # Trả về danh sách rỗng nếu có lỗi đọc

            except Exception as e:
                print(f"Lỗi khi đọc file log hoạt động {log_path} dữ liệu gần đây:\n{e}")
                # messagebox.showwarning("Lỗi Đọc Log", f"Lỗi khi đọc file log hoạt động để phân tích:\n{e}", parent=self.root)
                return [] # Trả về danh sách rỗng nếu có lỗi đọc

        # Sắp xếp các bản ghi theo thời gian (từ cũ đến mới) nếu cần thiết cho phân tích xu hướng,
        # nhưng cho việc tính % thì không bắt buộc. Giữ nguyên thứ tự đọc từ file.
        # recent_logs.sort(key=lambda x: datetime.datetime.strptime(x.get("timestamp"), "%Y-%m-%d %H:%M:%S"))

        return recent_logs

    def calculate_behavior_emotion_percentages(self, logs):
        """
        Tính tỷ lệ phần trăm các label Cảm xúc (Tích cực/Tiêu cực/Trung tính)
        và Phân loại Hành vi (Có ích/Không có ích) trong danh sách log đã cho.
        Trả về dictionary chứa các tỷ lệ.
        """
        total_logs = len(logs)
        if total_logs == 0:
            return {
                'total_logs': 0,
                'positive_emotion_pct': 0,
                'negative_emotion_pct': 0,
                'neutral_emotion_pct': 0, # Vẫn giữ cho Cảm xúc
                'productive_behavior_pct': 0,
                'unproductive_behavior_pct': 0,
                # 'other_behavior_pct': 0, # Bỏ phần này
            }

        # Đếm số lần xuất hiện của từng loại label
        positive_emotion_count = 0
        negative_emotion_count = 0
        neutral_emotion_count = 0

        productive_behavior_count = 0
        unproductive_behavior_count = 0
        # other_behavior_count = 0 # Bỏ phần này

        for entry in logs:
            emotion = entry.get("emotion")
            category = entry.get("category")

            if emotion in POSITIVE_EMOTIONS:
                positive_emotion_count += 1
            elif emotion in NEGATIVE_EMOTIONS:
                negative_emotion_count += 1
            elif emotion == "Bình thường":
                 neutral_emotion_count += 1

            if category in PRODUCTIVE_BEHAVIORS:
                productive_behavior_count += 1
            elif category in UNPRODUCTIVE_BEHAVIORS:
                unproductive_behavior_count += 1
            # --- Bỏ phần kiểm tra category không thuộc 2 nhóm trên ---
            # else:
            #      other_behavior_count += 1
            # -------------------------------------------------------


        # Tính phần trăm
        positive_emotion_pct = (positive_emotion_count / total_logs) * 100
        negative_emotion_pct = (negative_emotion_count / total_logs) * 100
        neutral_emotion_pct = (neutral_emotion_count / total_logs) * 100

        productive_behavior_pct = (productive_behavior_count / total_logs) * 100
        unproductive_behavior_pct = (unproductive_behavior_count / total_logs) * 100
        # other_behavior_pct = (other_behavior_count / total_logs) * 100 # Bỏ phần này


        return {
            'total_logs': total_logs,
            'positive_emotion_pct': round(positive_emotion_pct, 1),
            'negative_emotion_pct': round(negative_emotion_pct, 1),
            'neutral_emotion_pct': round(neutral_emotion_pct, 1),
            'productive_behavior_pct': round(productive_behavior_pct, 1),
            'unproductive_behavior_pct': round(unproductive_behavior_pct, 1),
            # 'other_behavior_pct': round(other_behavior_pct, 1), # Bỏ phần này
        }

# Phương thức get_performance_indicators và ask_question sẽ sử dụng kết quả từ hàm này
# nên chúng không cần sửa đổi về mặt logic tính toán percentage, chỉ cần đảm bảo
# chúng sử dụng các khóa percentage đúng (positive_emotion_pct, negative_emotion_pct,
# productive_behavior_pct, unproductive_behavior_pct).
# Logic tính overall_negative/positive trong get_performance_indicators đã dùng đúng các khóa này.
    
    def get_performance_indicators(self):
        """
        Thực hiện phân tích log hoạt động theo các quy tắc và xác định các indicator.
        Trả về dictionary chứa kết quả để hiển thị.
        """
        # Lấy log hoạt động cho 3 khung thời gian
        logs_1day = self.get_recent_activity_logs(1)
        logs_3days = self.get_recent_activity_logs(3)
        logs_7days = self.get_recent_activity_logs(7) # Dùng cho quy tắc 1 trên tuần (nếu cần)

        # Tính phần trăm cho từng khung thời gian
        pct_1day = self.calculate_behavior_emotion_percentages(logs_1day)
        pct_3days = self.calculate_behavior_emotion_percentages(logs_3days)
        pct_7days = self.calculate_behavior_emotion_percentages(logs_7days)


        # --- Áp dụng Quy tắc 1: Icon cảnh báo/khen ngợi chung (ví dụ dựa trên 1 ngày gần nhất) ---
        # Bạn muốn dựa trên Cảm xúc hay Hành vi hay cả hai?
        # Dựa trên mô tả, có vẻ quy tắc 1 là về TỔNG THỂ trạng thái và hành vi gần đây.
        # Hãy kết hợp cảm xúc tiêu cực và hành vi không có ích làm "tiêu cực tổng thể".
        # Kết hợp cảm xúc tích cực và hành vi có ích làm "tích cực tổng thể".

        # Tỷ lệ tiêu cực/tích cực tổng thể trong 1 ngày
        overall_negative_1day = pct_1day['negative_emotion_pct'] + pct_1day['unproductive_behavior_pct']
        overall_positive_1day = pct_1day['positive_emotion_pct'] + pct_1day['productive_behavior_pct']

        main_status_icon = "" # Icon chính
        main_status_message = "" # Thông báo chính

        # Điều chỉnh ngưỡng và logic dựa trên ý muốn cụ thể của bạn
        # Ví dụ: Chỉ cần 1 trong 2 nhóm (cảm xúc tiêu cực HOẶC hành vi không ích) vượt 50% là cảnh báo?
        # Hoặc tổng cả hai vượt 50%?
        # Giả định: Nếu TỔNG CẢM XÚC TIÊU CỰC VÀ HÀNH VI KHÔNG ÍCH trong 1 ngày > 50% => Cảnh báo đỏ
        # Giả định: Nếu TỔNG CẢM XÚC TÍCH CỰC VÀ HÀNH VI CÓ ÍCH trong 1 ngày > 50% => Khen ngợi xanh
        # Nếu cả hai không đạt ngưỡng, có thể hiển thị trạng thái trung tính hoặc thông tin chi tiết hơn.

        # Cảnh báo đỏ nếu tổng tiêu cực + không ích > 50% trong 1 ngày (hoặc ngưỡng khác)
        # Bạn có thể muốn ngưỡng cao hơn, ví dụ 60% hoặc 70% để cảnh báo thật sự nghiêm trọng.
        # Hãy dùng ngưỡng 50% như bạn nói.
        if overall_negative_1day > 50:
             main_status_icon = "🔴" # Icon đỏ
             main_status_message = "Cần chú ý: Xu hướng tiêu cực/không hiệu quả gần đây."
        # Khen ngợi xanh nếu tổng tích cực + có ích > 50% trong 1 ngày (hoặc ngưỡng khác)
        elif overall_positive_1day > 50:
             main_status_icon = "🟢" # Icon xanh lá
             main_status_message = "Tuyệt vời! Xu hướng tích cực/hiệu quả gần đây."
        else:
             main_status_icon = "⚪" # Icon trắng/xám (trung tính)
             main_status_message = "Hoạt động gần đây ở mức cân bằng."

        # Có thể thêm chi tiết % vào message nếu muốn
        # main_status_message += f" (Tiêu cực/Không ích: {overall_negative_1day:.1f}%, Tích cực/Có ích: {overall_positive_1day:.1f}%)"


        # --- Áp dụng Quy tắc 2: Icon xu hướng (lên/xuống) ---
        # So sánh % tiêu cực của 1 ngày so với 3 ngày
        # So sánh % tích cực của 1 ngày so với 3 ngày
        # Có nhiều cách định nghĩa "xu hướng đi lên/đi xuống".
        # Ví dụ:
        # - Xu hướng tiêu cực đi lên: % tiêu cực hôm nay > % tiêu cực 3 ngày
        # - Xu hướng tích cực đi lên: % tích cực hôm nay > % tích cực 3 ngày
        # Làm thế nào để kết hợp cả hai?
        # Một cách là so sánh "điểm số" tiêu cực/tích cực tổng thể giữa 1 ngày và 3 ngày.
        # Ví dụ: (Tích cực - Tiêu cực) của 1 ngày so với (Tích cực - Tiêu cực) của 3 ngày.
        # Nếu (Pos_1d - Neg_1d) > (Pos_3d - Neg_3d) => Điểm số đang tăng => Xu hướng đi lên (mũi tên xanh)
        # Nếu (Pos_1d - Neg_1d) < (Pos_3d - Neg_3d) => Điểm số đang giảm => Xu hướng đi xuống (mũi tên đỏ)

        # Tính điểm số (Tích cực - Tiêu cực)
        score_1day = pct_1day['positive_emotion_pct'] + pct_1day['productive_behavior_pct'] - (pct_1day['negative_emotion_pct'] + pct_1day['unproductive_behavior_pct'])
        score_3days = pct_3days['positive_emotion_pct'] + pct_3days['productive_behavior_pct'] - (pct_3days['negative_emotion_pct'] + pct_3days['unproductive_behavior_pct'])


        trend_icon = "⚪" # Icon xu hướng mặc định (trung tính)
        # Chỉ xác định xu hướng nếu có đủ dữ liệu (ít nhất 2 điểm dữ liệu: hôm nay và trong 3 ngày)
        # và có sự thay đổi đáng kể (tránh nhiễu nhỏ)
        # Ví dụ: Nếu có ít nhất 5 bản ghi trong 3 ngày và ít nhất 2 bản ghi trong 1 ngày
        # và sự chênh lệch điểm số đủ lớn (ví dụ > 5 hoặc 10 điểm %)

        # Đảm bảo có đủ dữ liệu trong cả 1 ngày và 3 ngày để so sánh
        if pct_1day['total_logs'] >= 2 and pct_3days['total_logs'] >= 5: # Ngưỡng dữ liệu tối thiểu

            # So sánh điểm số để xác định xu hướng
            if score_1day > score_3days:
                 # Xu hướng tốt hơn (đi lên)
                 trend_icon = "⬆️" # Mũi tên xanh lá (có thể đổi thành mũi tên màu xanh)
                 # Có thể thêm một thông báo xu hướng cụ thể nếu cần
            elif score_1day < score_3days:
                 # Xu hướng xấu đi (đi xuống)
                 trend_icon = "⬇️" # Mũi tên đỏ (có thể đổi thành mũi tên màu đỏ)
                 # Có thể thêm một thông báo xu hướng cụ thể nếu cần
            else:
                 # Điểm số bằng nhau hoặc không thay đổi đáng kể
                 trend_icon = "➡️" # Mũi tên ngang (ổn định)


        # --- Kết quả cuối cùng để hiển thị ---
        return {
            'main_status_icon': main_status_icon,
            'main_status_message': main_status_message,
            'trend_icon': trend_icon,
            # Có thể trả về thêm các chi tiết % nếu muốn hiển thị chi tiết hơn trên popup
            # 'pct_1day': pct_1day,
            # 'pct_3days': pct_3days,
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_program)
    root.mainloop()