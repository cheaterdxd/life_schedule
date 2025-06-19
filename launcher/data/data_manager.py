import json
import os

class DataManager:
    """Quản lý việc đọc và ghi dữ liệu sách vào file JSON."""
    def __init__(self, file_path='books.json'):
        self.file_path = file_path

    def load_books(self):
        if not os.path.exists(self.file_path):
            return []
        # Thêm xử lý file rỗng
        if os.path.getsize(self.file_path) == 0:
            return []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return []

    def save_books(self, books_data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, ensure_ascii=False, indent=4)
