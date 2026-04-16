import json
import hashlib
import uuid
from datetime import datetime
import os

# ==================== 用户管理（新增头像字段） ====================
class UserManager:
    def __init__(self):
        self.file = "users_data.json"
        self.load()

    def load(self):
        """加载用户数据"""
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def save(self):
        """保存用户数据"""
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def hash_pwd(self, pwd):
        """密码哈希加密"""
        return hashlib.sha256(pwd.encode()).hexdigest()

    def register_user(self, username, password):
        """用户注册"""
        if username in self.data:
            return False
        self.data[username] = {
            "user_id": str(uuid.uuid4()),
            "username": username,
            "password": self.hash_pwd(password),
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "avatar_path": None  # 新增头像路径字段
        }
        self.save()
        return True

    def login_user(self, username, password):
        """用户登录"""
        if username not in self.data:
            return None
        if self.data[username]["password"] == self.hash_pwd(password):
            # 更新上次登录时间
            self.data[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.save()
            return self.data[username]
        return None

    def update_avatar(self, user_id, avatar_path):
        """更新用户头像路径"""
        for username, user in self.data.items():
            if user["user_id"] == user_id:
                user["avatar_path"] = avatar_path
                self.save()
                return True
        return False

# ==================== 笔记管理（完善增删改查） ====================
class NoteManager:
    def __init__(self):
        self.file = "notes_data.json"
        self.load()

    def load(self):
        """加载笔记数据"""
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
        except FileNotFoundError:
            self.notes = []

    def save(self):
        """保存笔记数据"""
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)

    def add_note(self, user_id, title, content, category, tags):
        """新增笔记"""
        note = {
            "note_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.notes.append(note)
        self.save()
        return note

    def get_user_notes(self, user_id):
        """获取用户所有笔记（按更新时间倒序）"""
        user_notes = [n for n in self.notes if n["user_id"] == user_id]
        user_notes.sort(key=lambda x: x["update_time"], reverse=True)
        return user_notes

    def get_note_by_id(self, note_id, user_id):
        """根据ID获取笔记"""
        for n in self.notes:
            if n["note_id"] == note_id and n["user_id"] == user_id:
                return n
        return None

    def update_note(self, note_id, user_id, title, content, category, tags):
        """更新笔记"""
        for n in self.notes:
            if n["note_id"] == note_id and n["user_id"] == user_id:
                n["title"] = title
                n["content"] = content
                n["category"] = category
                n["tags"] = tags
                n["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save()
                return True
        return False

    def delete_note(self, note_id, user_id):
        """删除笔记"""
        self.notes = [n for n in self.notes if not (n["note_id"] == note_id and n["user_id"] == user_id)]
        self.save()
        return True

    def get_all_categories(self, user_id):
        """获取用户所有分类"""
        cats = [n["category"] for n in self.get_user_notes(user_id)]
        return list(set(cats))

    def get_all_tags(self, user_id):
        """获取用户所有标签"""
        tags = []
        for n in self.get_user_notes(user_id):
            tags.extend(n["tags"])
        return list(set(tags))

# 实例化管理器（全局单例）
user_manager = UserManager()
note_manager = NoteManager()