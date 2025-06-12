import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import platform
import csv
import os

class PomodoroApp:
    def __init__(self, master):
        self.master = master
        master.title("Pomodoro Focus") 
        # Tăng đáng kể chiều cao tổng thể của cửa sổ
        master.geometry("350x300") # Chiều rộng giữ nguyên, chiều cao tăng từ 350 lên 400
        master.resizable(True, True)
        
        # Bảng màu Flat Dark Mode (giữ nguyên, thêm màu xanh cho panel)
        self.COLOR_BG_PRIMARY = "#2C2C2C"     
        self.COLOR_BG_SECONDARY = "#3C3C3C"   
        self.COLOR_TEXT_LIGHT = "#E0E0E0"     
        self.COLOR_ACCENT_GREEN = "#69F0AE"   
        self.COLOR_ACCENT_BLUE = "#40C4FF"    
        self.COLOR_ACCENT_YELLOW = "#FFD740"  
        self.COLOR_ACCENT_RED = "#FF5252"     
        self.COLOR_PRIMARY_BUTTON = "#536DFE" 
        self.COLOR_LONG_BREAK_ORANGE = "#FFAB40" 
        self.COLOR_BLUE_PANEL = "#1E88E5"  # Màu xanh nổi bật cho panel nút

        master.config(bg=self.COLOR_BG_PRIMARY)

        # Cấu hình Themed Tkinter (ttk)
        style = ttk.Style()
        style.theme_use("clam") 

        style.configure("TLabel", background=self.COLOR_BG_PRIMARY, foreground=self.COLOR_TEXT_LIGHT)
        
        # Cấu hình chung cho tất cả các nút icon
        style.configure("IconButton.TButton", 
                        background=self.COLOR_BLUE_PANEL, 
                        foreground="white", 
                        relief="flat",      
                        borderwidth=0,      
                        padding=[8, 8, 8, 8] 
                        ) 
        style.map("IconButton.TButton",
                  background=[('active', "#2196F3"), ('disabled', self.COLOR_BLUE_PANEL)], 
                  foreground=[('disabled', '#A0A0A0')])
        

        self.work_time = 25 * 60
        self.short_break_time = 5 * 60
        self.long_break_time = 15 * 60

        self.current_time = self.work_time
        self.is_running = False
        self.on_work = True
        self.cycles = 0
        self.master.after_id = None
        self.current_task = ""

        self.paused_time_left = 0
        self.paused_task = ""
        self.is_paused = False

        # Tải các icon (đảm bảo các file này có trong cùng thư mục và có kích thước 64x64)
        try:
            self.icon_play = tk.PhotoImage(file="play_icon.png")
            self.icon_pause = tk.PhotoImage(file="pause_icon.png")
            self.icon_refresh = tk.PhotoImage(file="refresh_icon.png")
            self.icon_forward = tk.PhotoImage(file="forward_icon.png")
            
        except tk.TclError:
            messagebox.showerror("Lỗi Icon", "Không tìm thấy các tệp icon (play_icon.png, pause_icon.png, refresh_icon.png, forward_icon.png). Vui lòng đặt chúng cùng thư mục với tệp Python.")
            self.master.destroy() 
            return

        # --- Giao diện người dùng ---
        # 1. Cấu hình lưới chính của cửa sổ
        # Hàng 0: 4/5 chiều cao (tỉ lệ 4) cho nút và đồng hồ
        # Hàng 1: 1/5 chiều cao (tỉ lệ 1) cho thanh trạng thái
        # Tăng weight của hàng 1 (status) để nó nhận được nhiều không gian hơn
        self.master.rowconfigure(0, weight=4) 
        self.master.rowconfigure(1, weight=1) # Giữ nguyên tỉ lệ để status vẫn là 1/5

        self.master.columnconfigure(0, weight=1) 
        self.master.columnconfigure(1, weight=2) 

        # 2. Panel chứa các nút (1/3 bên trái, màu xanh)
        self.panel_buttons = tk.Frame(master, bg=self.COLOR_BLUE_PANEL) 
        self.panel_buttons.grid(row=0, column=0, padx=0, pady=(0, 0), sticky="nsew") 
        
        self.panel_buttons.grid_columnconfigure(0, weight=1)
        self.panel_buttons.grid_rowconfigure(0, weight=1)
        self.panel_buttons.grid_rowconfigure(1, weight=1)
        self.panel_buttons.grid_rowconfigure(2, weight=1)
        self.panel_buttons.grid_rowconfigure(3, weight=1)


        # 3. Frame chứa đồng hồ đếm giờ (2/3 bên phải)
        self.frame_timer_right = tk.Frame(master, bg=self.COLOR_BG_PRIMARY)
        self.frame_timer_right.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="nsew")
        
        self.frame_timer_right.grid_columnconfigure(0, weight=1)
        self.frame_timer_right.grid_rowconfigure(0, weight=1)
        
        self.label_timer = ttk.Label(self.frame_timer_right, text="25:00", font=("Roboto", 64, "bold"), 
                                    foreground=self.COLOR_ACCENT_GREEN, background=self.COLOR_BG_PRIMARY)
        self.label_timer.grid(row=0, column=0, sticky="") 

        # --- Nút điều khiển trong panel_buttons (sử dụng icon) ---
        button_pad_x = 5
        button_pad_y = 5

        self.btn_start = ttk.Button(self.panel_buttons, image=self.icon_play, command=self.prompt_and_start_timer, 
                                   style="IconButton.TButton") 
        self.btn_start.grid(row=0, column=0, padx=button_pad_x, pady=button_pad_y, sticky="ew")

        self.btn_stop = ttk.Button(self.panel_buttons, image=self.icon_pause, command=self.stop_timer, 
                                  style="IconButton.TButton")
        self.btn_stop.grid(row=1, column=0, padx=button_pad_x, pady=button_pad_y, sticky="ew")

        self.btn_reset = ttk.Button(self.panel_buttons, image=self.icon_refresh, command=self.reset_timer, 
                                   style="IconButton.TButton")
        self.btn_reset.grid(row=2, column=0, padx=button_pad_x, pady=button_pad_y, sticky="ew")
        
        self.btn_continue = ttk.Button(self.panel_buttons, image=self.icon_forward, command=self.continue_timer, 
                                      style="IconButton.TButton", state=tk.DISABLED)
        self.btn_continue.grid(row=3, column=0, padx=button_pad_x, pady=button_pad_y, sticky="ew")

        # 4. Label hiển thị trạng thái (1/5 phía dưới)
        # Tăng font size của label status để nó hiển thị to hơn và rõ ràng hơn
        self.label_status = ttk.Label(master, text="Work Time", font=("Roboto", 18), # Tăng font size từ 14 lên 18
                                     foreground=self.COLOR_TEXT_LIGHT, background=self.COLOR_BG_PRIMARY,
                                     anchor="center") 
        self.label_status.grid(row=1, column=0, columnspan=2, pady=(5, 15), sticky="ew") 

        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.label_timer.config(text=time_str)

    def prompt_and_start_timer(self):
        if self.is_paused and self.on_work:
            messagebox.showinfo("Pomodoro", "Hãy sử dụng nút 'Continue' để tiếp tục công việc bị dừng.")
            return

        if not self.is_running and self.on_work:
            task = simpledialog.askstring("Pomodoro", "Bạn sẽ làm gì trong 25 phút tới?", parent=self.master)
            if task:
                self.current_task = task
                self.start_timer()
                self.log_action(self.current_task, "Starting")
                self.label_status.config(text=f"Task: {self.current_task}", foreground=self.COLOR_TEXT_LIGHT)
            else:
                self.label_status.config(text="Start cancelled", foreground=self.COLOR_ACCENT_RED)
        elif not self.is_running and not self.on_work:
            self.label_status.config(text="Still on break", foreground=self.COLOR_ACCENT_BLUE)
        elif self.is_running:
            self.label_status.config(text="Timer already running!", foreground=self.COLOR_ACCENT_YELLOW)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.btn_continue.config(state=tk.DISABLED)
            self.countdown()

    def stop_timer(self):
        if self.is_running:
            self.log_action(self.current_task, "Stopped")
            self.paused_time_left = self.current_time
            self.paused_task = self.current_task
            self.is_paused = True
            self.btn_continue.config(state=tk.NORMAL)
            self.label_status.config(text="Timer Stopped", foreground=self.COLOR_ACCENT_YELLOW)
        else:
            self.label_status.config(text="Already stopped", foreground=self.COLOR_ACCENT_YELLOW)

        self.is_running = False
        if self.master.after_id:
            self.master.after_cancel(self.master.after_id)
        self.master.after_id = None

    def continue_timer(self):
        if self.is_paused:
            self.current_time = self.paused_time_left
            self.current_task = self.paused_task
            self.is_paused = False
            
            self.log_action(self.current_task, "Continuing")
            self.start_timer()
            self.update_timer_display()
            self.label_status.config(text=f"Continuing: {self.current_task}", foreground=self.COLOR_ACCENT_BLUE)
        else:
            self.label_status.config(text="Nothing to continue", foreground=self.COLOR_ACCENT_RED)

    def reset_timer(self):
        self.stop_timer() 
        self.current_time = self.work_time
        self.on_work = True
        self.cycles = 0
        self.current_task = ""
        
        self.paused_time_left = 0
        self.paused_task = ""
        self.is_paused = False
        self.btn_continue.config(state=tk.DISABLED)

        self.label_status.config(text="Work Time", foreground=self.COLOR_TEXT_LIGHT)
        self.label_timer.config(foreground=self.COLOR_ACCENT_GREEN)
        self.update_timer_display()
        self.label_status.config(text="Timer Reset", foreground=self.COLOR_ACCENT_RED)

    def countdown(self):
        if self.is_running and self.current_time > 0:
            self.current_time -= 1
            self.update_timer_display()
            self.master.after_id = self.master.after(1000, self.countdown)
        elif self.is_running and self.current_time == 0:
            self.switch_mode()

    def switch_mode(self):
        if self.on_work:
            self.log_action(self.current_task, "Completed")

        self.is_running_temp = self.is_running 
        self.is_running = False 
        self.stop_timer() 
        self.is_running = self.is_running_temp 
        
        if self.master.after_id:
            self.master.after_cancel(self.master.after_id)
        self.master.after_id = None

        if self.on_work:
            self.cycles += 1
            if self.cycles % 4 == 0:
                self.current_time = self.long_break_time
                self.label_status.config(text="Long Break", foreground=self.COLOR_LONG_BREAK_ORANGE)
                self.label_timer.config(foreground=self.COLOR_LONG_BREAK_ORANGE)
                messagebox.showinfo("Pomodoro", "Work time finished! Take a long break.")
            else:
                self.current_time = self.short_break_time
                self.label_status.config(text="Short Break", foreground=self.COLOR_ACCENT_BLUE)
                self.label_timer.config(foreground=self.COLOR_ACCENT_BLUE)
                messagebox.showinfo("Pomodoro", "Work time finished! Take a short break.")
            self.on_work = False
            self.current_task = ""
            self.is_paused = False 
            self.btn_continue.config(state=tk.DISABLED)

        else:
            self.current_time = self.work_time
            self.label_status.config(text="Work Time", foreground=self.COLOR_TEXT_LIGHT)
            self.label_timer.config(foreground=self.COLOR_ACCENT_GREEN)
            messagebox.showinfo("Pomodoro", "Break finished! Time to work.")
            self.on_work = True
            self.is_paused = False 
            self.btn_continue.config(state=tk.DISABLED)

        self.update_timer_display()

    def log_action(self, task, status):
        log_file = "pomodoro_log.csv"
        file_exists = os.path.isfile(log_file)

        now = datetime.datetime.now()
        log_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

        data = [
            log_time_str,
            task,
            status
        ]

        try:
            with open(log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Log Time", "Task", "Status"])
                writer.writerow(data)
            print(f"Logged to CSV: {data}")
        except Exception as e:
            messagebox.showerror("File Error", f"Cannot write to log file: {e}")

root = tk.Tk()
app = PomodoroApp(root)
root.mainloop()