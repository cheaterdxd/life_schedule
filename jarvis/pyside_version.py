# -*- coding: utf-8 -*-
"""
Trình Nhắc Nhở Hoạt Động & Nhiệm vụ - Phiên bản Flat UI (PySide6)
-----------------------------------------------------------------
Giao diện được thiết kế lại theo phong cách phẳng, hiện đại sử dụng Qt Style Sheets.
"""
import sys
import os
import time
import datetime
import json
import threading

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QDialog, QLineEdit, QComboBox, QMessageBox, QInputDialog, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, QTime, Signal
from PySide6.QtGui import QIcon, QFont, QCloseEvent

try:
    from playsound3 import playsound
except ImportError:
    app_temp = QApplication(sys.argv)
    QMessageBox.critical(None, "Lỗi thiếu thư viện", "Vui lòng cài đặt thư viện playsound3: pip install playsound3")
    sys.exit(1)

# --- Các hằng số và cấu hình (Giữ nguyên) ---
DEFAULT_INTERVAL_MINUTES = 15
ACTIVITY_LOG_FILE = "activity_log.json"
SOUND_FILE = "clockbeep.wav"
ALERT_SOUND = "alert.wav"
TODO_FILE_PREFIX = "todolist_"
EMOTION_LABELS = ["Vui", "Rất vui", "Hạnh phúc", "Hạnh phúc Viên mãn", "Bình thường", "Giận dữ", "Sầu muộn", "Rối trí", "Hổ thẹn"]
POSITIVE_EMOTIONS = ["Vui", "Rất vui", "Hạnh phúc", "Hạnh phúc Viên mãn"]
NEGATIVE_EMOTIONS = ["Giận dữ", "Sầu muộn", "Rối trí", "Hổ thẹn"]
BEHAVIOR_CATEGORIES = ["Nghiên cứu có ích", "Đọc có ích", "Viết có ích", "Nói/ Thuyết giảng có ích", "Nghiên cứu không có ích", "Đọc không có ích", "Viết không có ích", "Nói/ Thuyết giảng không có ích", "Mất tập trung vào nhiệm vụ hiện tại", "Buồn ngủ khi đang làm việc", "Chơi game"]
PRODUCTIVE_BEHAVIORS = ["Nghiên cứu có ích", "Đọc có ích", "Viết có ích", "Nói/ Thuyết giảng có ích"]
UNPRODUCTIVE_BEHAVIORS = ["Nghiên cứu không có ích", "Đọc không có ích", "Viết không có ích", "Nói/ Thuyết giảng không có ích", "Mất tập trung vào nhiệm vụ hiện tại", "Buồn ngủ khi đang làm việc", "Chơi game"]
# ---------------------------------------------------

# =========================================================================
# === BẢNG KIỂU GIAO DIỆN PHẲNG (FLAT UI STYLESHEET) ===
# =========================================================================
FLAT_STYLE_SHEET = """
    /* --- Nền chung cho Cửa sổ và Dialog --- */
    QMainWindow, QDialog {
        background-color: #2c313c;
    }

    /* --- Nhãn (Label) --- */
    QLabel {
        color: #f0f0f0;
        font-size: 11pt;
    }
    QLabel#StatusLabel { /* Nhãn trạng thái chính */
        font-size: 14pt;
        font-weight: bold;
    }

    /* --- Nút bấm (Button) --- */
    QPushButton {
        color: #f0f0f0;
        background-color: #4a5160;
        border: none;
        padding: 8px 16px;
        font-size: 11pt;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5b6375;
    }
    QPushButton:pressed {
        background-color: #3e92cc;
    }
    /* Các nút đặc biệt */
    QPushButton#TasksButton {
        background-color: #fca311;
        color: #14213d;
        font-weight: bold;
    }
    QPushButton#TasksButton:hover {
        background-color: #ffb74d;
    }
    QPushButton#StopButton {
        background-color: #c0392b;
    }
    QPushButton#StopButton:hover {
        background-color: #e74c3c;
    }
    QPushButton#SubmitButton {
        background-color: #27ae60;
    }
    QPushButton#SubmitButton:hover {
        background-color: #2ecc71;
    }

    /* --- Ô nhập liệu (LineEdit) --- */
    QLineEdit {
        background-color: #343b48;
        color: #f0f0f0;
        border: 1px solid #4a5160;
        border-radius: 5px;
        padding: 8px;
        font-size: 11pt;
    }
    QLineEdit:focus {
        border: 1px solid #3e92cc;
    }

    /* --- Hộp chọn (ComboBox) --- */
    QComboBox {
        background-color: #343b48;
        color: #f0f0f0;
        border: 1px solid #4a5160;
        border-radius: 5px;
        padding: 8px;
    }
    QComboBox:hover {
        border: 1px solid #5b6375;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: url(down_arrow.png); /* Bạn cần có file down_arrow.png hoặc xóa dòng này */
    }
    QComboBox QAbstractItemView { /* Kiểu cho danh sách xổ xuống */
        background-color: #343b48;
        color: #f0f0f0;
        border: 1px solid #4a5160;
        selection-background-color: #3e92cc;
        outline: 0px;
    }

    /* --- Thanh cuộn (ScrollBar) --- */
    QScrollBar:vertical {
        border: none;
        background: #2c313c;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #4a5160;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #5b6375;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }

    /* --- Vùng cuộn (ScrollArea) --- */
    QScrollArea {
        border: none;
    }

    /* --- Hộp thông báo (MessageBox) --- */
    QMessageBox {
        background-color: #343b48;
    }
    QMessageBox QLabel {
        color: #f0f0f0;
        font-size: 11pt;
    }
"""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ReminderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trình Nhắc Nhở Hoạt Động & Nhiệm vụ")
        self.setMinimumSize(500, 220)

        # Trạng thái
        self.reminder_interval_ms = DEFAULT_INTERVAL_MINUTES * 60 * 1000
        self.sleep_until_time = 0
        self.is_running = True
        self.tasks = []
        self.reminder_timer = QTimer(self)
        self.countdown_timer = QTimer(self)

        # Âm thanh và Icon
        self.sound_path = resource_path(SOUND_FILE)
        self.alert_sound_path = resource_path(ALERT_SOUND)
        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Giao diện
        self.setup_ui()

        # Logic
        self.ensure_activity_log_file()
        self.initialize_tasks()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.status_label = QLabel("Đang chạy...")
        self.status_label.setObjectName("StatusLabel") # Đặt tên để style riêng
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.last_check_label = QLabel("Chưa có lần kiểm tra hoạt động nào.")
        self.last_check_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.last_check_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        sleep_btn = QPushButton("😴 Đi ngủ")
        sleep_btn.clicked.connect(self.go_to_sleep)
        button_layout.addWidget(sleep_btn)

        settings_btn = QPushButton("⚙️ Cài đặt")
        settings_btn.clicked.connect(self.change_interval)
        button_layout.addWidget(settings_btn)

        tasks_btn = QPushButton("📝 Nhiệm vụ")
        tasks_btn.setObjectName("TasksButton") # Đặt tên để style riêng
        tasks_btn.clicked.connect(self.show_task_window)
        button_layout.addWidget(tasks_btn)

        stop_btn = QPushButton("⏹️ Dừng")
        stop_btn.setObjectName("StopButton") # Đặt tên để style riêng
        stop_btn.clicked.connect(self.close)
        button_layout.addWidget(stop_btn)

        main_layout.addLayout(button_layout)

    # --- Các hàm logic, không thay đổi so với phiên bản trước ---
    # ... (để tránh lặp lại, các hàm này được giữ nguyên như file trước)
    #
    def ensure_activity_log_file(self):
        log_path = resource_path(ACTIVITY_LOG_FILE)
        if not os.path.exists(log_path):
            try:
                with open(log_path, 'w', encoding='utf-8') as f: json.dump([], f)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi File Log", f"Không thể tạo file {ACTIVITY_LOG_FILE}:\n{e}")
                self.is_running = False

    def save_log(self, answer, emotion, category):
        log_path = resource_path(ACTIVITY_LOG_FILE)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {"timestamp": timestamp, "activity": answer, "emotion": emotion, "category": category}
        log_data = []
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content: log_data = json.loads(content)
            except Exception as e: QMessageBox.warning(self, "Lỗi Đọc Log", f"Không thể đọc file log:\n{e}")
        log_data.append(new_entry)
        try:
            with open(log_path, 'w', encoding='utf-8') as f: json.dump(log_data, f, ensure_ascii=False, indent=4)
            self.last_check_label.setText(f"Lần cuối kiểm tra lúc: {timestamp}")
        except Exception as e: QMessageBox.warning(self, "Lỗi Ghi Log", f"Không thể ghi file log:\n{e}")

    def play_sound_in_thread(self, sound_path):
        if os.path.exists(sound_path):
            threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

    def schedule_next_reminder(self):
        if self.reminder_timer.isActive(): self.reminder_timer.stop()
        if not self.is_running: return
        if time.time() >= self.sleep_until_time:
            self.reminder_timer.setSingleShot(True)
            self.reminder_timer.timeout.connect(self.ask_question)
            self.reminder_timer.start(self.reminder_interval_ms)
            if not self.countdown_timer.isActive(): self.status_label.setText(f"Sẽ nhắc nhở sau {self.reminder_interval_ms // 60000} phút")
        else:
            wake_up_delay = int((self.sleep_until_time - time.time()) * 1000)
            if wake_up_delay > 0:
                self.reminder_timer.setSingleShot(True)
                self.reminder_timer.timeout.connect(self.schedule_next_reminder)
                self.reminder_timer.start(wake_up_delay + 500)

    def ask_question(self):
        if not self.is_running or time.time() < self.sleep_until_time:
            if self.is_running: self.schedule_next_reminder()
            return
        self.play_sound_in_thread(self.sound_path)
        dlg = AskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            answer, emotion, category = dlg.get_result()
            self.save_log(answer, emotion, category)
        self.schedule_next_reminder()

    def go_to_sleep(self):
        if self.countdown_timer.isActive():
            QMessageBox.information(self, "Thông báo", "Đang trong chế độ ngủ rồi.")
            return
        minutes, ok = QInputDialog.getInt(self, "Đi ngủ", "Bạn muốn nghỉ trong bao nhiêu phút?", 15, 1, 1440)
        if ok:
            self.sleep_until_time = time.time() + minutes * 60
            if self.reminder_timer.isActive(): self.reminder_timer.stop()
            self.update_countdown()

    def update_countdown(self):
        remaining = int(self.sleep_until_time - time.time())
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            self.status_label.setText(f"😴 Đang ngủ: còn {mins:02d}:{secs:02d}")
            self.countdown_timer.setSingleShot(True)
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)
        else:
            self.countdown_timer.stop()
            self.status_label.setText("Đã thức dậy!")
            self.sleep_until_time = 0
            self.schedule_next_reminder()

    def change_interval(self):
        current = self.reminder_interval_ms // 60000
        new_minutes, ok = QInputDialog.getInt(self, "Cài đặt thời gian", f"Nhập khoảng thời gian (phút):", current, 1, 120)
        if ok and new_minutes != current:
            self.reminder_interval_ms = new_minutes * 60 * 1000
            if not self.countdown_timer.isActive(): self.schedule_next_reminder()

    def show_task_window(self):
        dlg = TaskWindow(self.tasks, self)
        dlg.task_marked_done.connect(self.mark_task_completed)
        dlg.add_new_task.connect(self.show_task_creation_window)
        dlg.exec()
        self.show_task_window() # Mở lại để refresh sau khi cửa sổ con đóng

    def show_task_creation_window(self):
        dlg = TaskCreationDialog(self)
        if dlg.exec() == QDialog.Accepted:
            new_tasks = dlg.get_new_tasks()
            if new_tasks:
                self.tasks.extend(new_tasks)
                self.save_todolist()
                self.cancel_all_task_alarms()
                self.schedule_task_alarms()

    def mark_task_completed(self, task_to_complete):
        for task in self.tasks:
            if task is task_to_complete and not task.get('completed', False):
                task['completed'] = True
                task['completion_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.cancel_task_alarm(task)
                self.save_todolist()
                return

    def get_recent_activity_logs(self, timeframe_days):
        log_path = resource_path(ACTIVITY_LOG_FILE)
        recent_logs = []
        if not os.path.exists(log_path): return []
        start_time = datetime.datetime.now() - datetime.timedelta(days=timeframe_days)
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                log_data = json.loads(content) if content else []
            for entry in log_data:
                try:
                    entry_time = datetime.datetime.strptime(entry.get("timestamp"), "%Y-%m-%d %H:%M:%S")
                    if entry_time >= start_time: recent_logs.append(entry)
                except (ValueError, TypeError): continue
        except Exception as e: print(f"Lỗi đọc log phân tích: {e}")
        return recent_logs

    def calculate_behavior_emotion_percentages(self, logs):
        total_logs = len(logs)
        if total_logs == 0: return {'positive_emotion_pct': 0, 'negative_emotion_pct': 0, 'productive_behavior_pct': 0, 'unproductive_behavior_pct': 0, 'total_logs': 0}
        counts = {'pos_emo': 0, 'neg_emo': 0, 'prod_beh': 0, 'unprod_beh': 0}
        for entry in logs:
            if entry.get("emotion") in POSITIVE_EMOTIONS: counts['pos_emo'] += 1
            elif entry.get("emotion") in NEGATIVE_EMOTIONS: counts['neg_emo'] += 1
            if entry.get("category") in PRODUCTIVE_BEHAVIORS: counts['prod_beh'] += 1
            elif entry.get("category") in UNPRODUCTIVE_BEHAVIORS: counts['unprod_beh'] += 1
        return {'positive_emotion_pct': (counts['pos_emo'] / total_logs) * 100, 'negative_emotion_pct': (counts['neg_emo'] / total_logs) * 100, 'productive_behavior_pct': (counts['prod_beh'] / total_logs) * 100, 'unproductive_behavior_pct': (counts['unprod_beh'] / total_logs) * 100, 'total_logs': total_logs}

    def get_performance_indicators(self):
        pct_1day = self.calculate_behavior_emotion_percentages(self.get_recent_activity_logs(1))
        pct_3days = self.calculate_behavior_emotion_percentages(self.get_recent_activity_logs(3))
        overall_negative_1day = pct_1day['negative_emotion_pct'] + pct_1day['unproductive_behavior_pct']
        overall_positive_1day = pct_1day['positive_emotion_pct'] + pct_1day['productive_behavior_pct']
        main_status_icon, main_status_message = "⚪", "Hoạt động cân bằng."
        if overall_negative_1day > 50: main_status_icon, main_status_message = "🔴", "Xu hướng tiêu cực/không hiệu quả."
        elif overall_positive_1day > 50: main_status_icon, main_status_message = "🟢", "Xu hướng tích cực/hiệu quả."
        score_1day = overall_positive_1day - overall_negative_1day
        score_3days = (pct_3days['positive_emotion_pct'] + pct_3days['productive_behavior_pct']) - (pct_3days['negative_emotion_pct'] + pct_3days['unproductive_behavior_pct'])
        trend_icon = "➡️"
        if pct_1day['total_logs'] >= 2 and pct_3days['total_logs'] >= 5:
            if score_1day > score_3days: trend_icon = "⬆️"
            elif score_1day < score_3days: trend_icon = "⬇️"
        return {'main_status_icon': main_status_icon, 'main_status_message': main_status_message, 'trend_icon': trend_icon}

    def initialize_tasks(self):
        if not self.check_and_load_todolist(): self.play_sound_in_thread(self.alert_sound_path)
        else: self.schedule_task_alarms()
        self.schedule_next_reminder()

    def get_today_todo_filepath(self):
        return resource_path(f"{TODO_FILE_PREFIX}{datetime.date.today().strftime('%Y%m%d')}.json")

    def check_and_load_todolist(self):
        filepath = self.get_today_todo_filepath()
        self.tasks = []
        if not os.path.exists(filepath): return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.tasks = json.loads(content) if content else []
            for task in self.tasks:
                task.setdefault('completed', False); task.setdefault('completion_time', None); task.setdefault('labels', []); task.setdefault('scheduled_time', task.get('time')); task['alarm_timer'] = None
            self.tasks = [t for t in self.tasks if 'name' in t and 'time' in t]
            return True
        except Exception: return False

    def save_todolist(self):
        filepath = self.get_today_todo_filepath()
        tasks_to_save = [t.copy() for t in self.tasks]
        for task in tasks_to_save: task.pop('alarm_timer', None)
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(tasks_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e: QMessageBox.critical(self, "Lỗi Lưu Nhiệm vụ", f"Không thể ghi file {filepath}:\n{e}")

    def schedule_task_alarms(self):
        now = datetime.datetime.now()
        for task in self.tasks:
            if not task.get('completed', False) and task.get('alarm_timer') is None:
                try:
                    task_dt = datetime.datetime.combine(now.date(), QTime.fromString(task.get('scheduled_time', task.get('time')), "HH:mm").toPython())
                    if task_dt > now:
                        delay_ms = int((task_dt - now).total_seconds() * 1000)
                        timer = QTimer(self); timer.setSingleShot(True); timer.timeout.connect(lambda t=task: self.trigger_task_alarm(t)); timer.start(delay_ms)
                        task['alarm_timer'] = timer
                except Exception as e: print(f"Lỗi lên lịch báo thức: {e}")

    def trigger_task_alarm(self, task):
        self.play_sound_in_thread(self.sound_path)
        QMessageBox.information(self, "⏰ Báo thức Nhiệm vụ", f"Đã đến giờ thực hiện:\n\n{task.get('name')}")
        task['alarm_timer'] = None

    def cancel_task_alarm(self, task):
        if task.get('alarm_timer') and task['alarm_timer'].isActive():
            task['alarm_timer'].stop(); task['alarm_timer'] = None

    def cancel_all_task_alarms(self):
        for task in self.tasks: self.cancel_task_alarm(task)

    def closeEvent(self, event: QCloseEvent):
        self.is_running = False
        if self.reminder_timer.isActive(): self.reminder_timer.stop()
        if self.countdown_timer.isActive(): self.countdown_timer.stop()
        self.cancel_all_task_alarms()
        event.accept()

# --- Các Dialog tùy chỉnh (Được style lại) ---
class AskDialog(QDialog):
    def __init__(self, parent: ReminderApp):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Nhập Hoạt động & Trạng thái")
        self.setModal(True)
        self.setMinimumSize(600, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        indicators = self.parent_app.get_performance_indicators()
        indicator_label = QLabel(f"{indicators['main_status_icon']} {indicators['main_status_message']} {indicators['trend_icon']}")
        indicator_label.setFont(QFont("Helvetica", 14)); indicator_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(indicator_label)

        interval_min = self.parent_app.reminder_interval_ms // 60000
        layout.addWidget(QLabel(f"Bạn đã làm gì trong {interval_min} phút qua?"))
        self.entry_activity = QLineEdit(); layout.addWidget(self.entry_activity)

        layout.addWidget(QLabel("Cảm xúc của bạn:"))
        self.combo_emotion = QComboBox(); self.combo_emotion.addItems(EMOTION_LABELS); layout.addWidget(self.combo_emotion)

        layout.addWidget(QLabel("Phân loại hành vi:"))
        self.combo_category = QComboBox(); self.combo_category.addItems(BEHAVIOR_CATEGORIES); layout.addWidget(self.combo_category)

        self.submit_button = QPushButton("Xác nhận"); self.submit_button.setObjectName("SubmitButton")
        self.submit_button.clicked.connect(self.custom_accept)
        layout.addSpacing(10); layout.addWidget(self.submit_button)
        self.entry_activity.setFocus()

    def custom_accept(self):
        if not self.entry_activity.text().strip(): return
        self.accept()

    def get_result(self):
        return (self.entry_activity.text().strip(), self.combo_emotion.currentText(), self.combo_category.currentText())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: return
        elif event.key() in [Qt.Key_Return, Qt.Key_Enter]: self.custom_accept()
        else: super().keyPressEvent(event)

class TaskWindow(QDialog):
    task_marked_done = Signal(dict); add_new_task = Signal()
    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.setWindowTitle(f"Nhiệm vụ hôm nay ({datetime.date.today().strftime('%d/%m/%Y')})")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(10, 10, 10, 10)
        btn_layout = QHBoxLayout()
        add_button = QPushButton("➕ Thêm Nhiệm vụ"); add_button.clicked.connect(self.add_new_task.emit); add_button.clicked.connect(self.accept)
        btn_layout.addWidget(add_button); btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); main_layout.addWidget(scroll)
        content_widget = QWidget(); scroll.setWidget(content_widget)
        vbox = QVBoxLayout(content_widget)

        if not self.tasks: vbox.addWidget(QLabel("Chưa có nhiệm vụ nào cho hôm nay."))
        for task in self.tasks:
            task_frame = QFrame()
            task_layout = QHBoxLayout(task_frame)
            status = "✅" if task.get('completed', False) else "⬜"
            task_text = f"{status} {task.get('time')} - {task.get('name')}"
            labels_text = ", ".join(task.get('labels', []))
            if labels_text: task_text += f"  [{labels_text}]"
            label = QLabel(task_text)
            if task.get('completed', False):
                font = label.font(); font.setStrikeOut(True); label.setFont(font); label.setStyleSheet("color: #888;")
            task_layout.addWidget(label); task_layout.addStretch()
            if not task.get('completed', False):
                btn = QPushButton("✓"); btn.setFixedWidth(50)
                btn.clicked.connect(lambda _, t=task: self.task_marked_done.emit(t))
                task_layout.addWidget(btn)
            vbox.addWidget(task_frame)
        vbox.addStretch()
        close_button = QPushButton("Đóng"); close_button.clicked.connect(self.accept); main_layout.addWidget(close_button)

class TaskCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._temp_tasks_to_add = []
        self.setWindowTitle("Tạo Nhiệm vụ mới"); self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self); layout.setSpacing(10); layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(QLabel("Tên Nhiệm vụ:")); self.name_entry = QLineEdit(); self.name_entry.setFocus(); layout.addWidget(self.name_entry)
        layout.addWidget(QLabel("Thời gian (HH:MM):")); self.time_entry = QLineEdit(); self.time_entry.setInputMask("99:99"); layout.addWidget(self.time_entry)
        layout.addWidget(QLabel("Nhãn (phân cách bởi dấu phẩy):")); self.labels_entry = QLineEdit(); layout.addWidget(self.labels_entry)
        add_btn = QPushButton("➕ Thêm vào danh sách"); add_btn.clicked.connect(self.add_task_to_temp_list); layout.addWidget(add_btn)
        self.temp_list_label = QLabel("Chưa có nhiệm vụ nào được thêm."); layout.addWidget(self.temp_list_label)
        btn_layout = QHBoxLayout(); save_btn = QPushButton("💾 Lưu"); save_btn.setObjectName("SubmitButton"); save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ Hủy"); cancel_btn.setObjectName("StopButton"); cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn); btn_layout.addWidget(cancel_btn); layout.addLayout(btn_layout)

    def add_task_to_temp_list(self):
        name = self.name_entry.text().strip(); time_str = self.time_entry.text().strip()
        if not name or not time_str: return
        labels = [label.strip() for label in self.labels_entry.text().strip().split(',') if label.strip()]
        self._temp_tasks_to_add.append({'name': name, 'time': time_str, 'scheduled_time': time_str, 'completed': False, 'completion_time': None, 'labels': labels})
        self.name_entry.clear(); self.time_entry.clear(); self.labels_entry.clear(); self.name_entry.setFocus()
        self.temp_list_label.setText(f"Đã thêm {len(self._temp_tasks_to_add)} nhiệm vụ.")

    def get_new_tasks(self):
        return self._temp_tasks_to_add

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(FLAT_STYLE_SHEET) # Áp dụng style cho toàn bộ ứng dụng
    window = ReminderApp()
    window.show()
    sys.exit(app.exec())
