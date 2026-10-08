import os
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import json
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
MANAGER_URL = "https://t.me/kudaletimbro"

def db():
    conn = sqlite3.connect("/tmp/users.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT
    )""")
    return conn

def telegram(method, payload):
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def handle_update(update):
    message = update.get("message", {})
    user = message.get("from", {})
    chat = message.get("chat", {})
    text = message.get("text", "")

    if not user or not chat or text != "/start":
        return

    conn = db()
    conn.execute(
        "INSERT OR IGNORE INTO users (telegram_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
        (user["id"], user.get("username"), user.get("first_name"), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    telegram("sendMessage", {
        "chat_id": chat["id"],
        "text": (
            "Привет! 💗\n\n"
            "Добро пожаловать в PHOENIX AGENCY!\n\n"
            "Мы рады, что ты заинтересовалась сотрудничеством с нами.\n\n"
            "Наш менеджер расскажет подробнее об условиях, "
            "ответит на твои вопросы и поможет сделать первые шаги.\n\n"
            "Будем рады видеть тебя в нашей команде! ✨"
        ),
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "💌 Связаться с менеджером", "url": MANAGER_URL}
            ]]
        }
    })

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = self.rfile.read(length)
        try:
            handle_update(json.loads(body))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PHOENIX AGENCY BOT OK")
