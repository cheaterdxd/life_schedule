import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
LOG_FILE = DATA_DIR / "activity_log.json"

# Đảm bảo thư mục data tồn tại
DATA_DIR.mkdir(exist_ok=True)

def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def load_activity_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_activity_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def log_activity(task_name, duration_minutes, date=None):
    """Ghi log hoạt động (Pomodoro) vào file."""
    from datetime import datetime
    log = load_activity_log()
    log.append({
        "task": task_name,
        "duration": duration_minutes,
        "date": date or datetime.now().strftime("%Y-%m-%d")
    })
    save_activity_log(log)
