import os
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
MANAGER_URL = "https://t.me/kudaletimbro"
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(user):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        INSERT OR IGNORE INTO users
        (telegram_id, username, first_name, joined_at)
        VALUES (?, ?, ?, ?)
    """, (user.id, user.username, user.first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    text = (
        "Привет! 💗\n\n"
        "Добро пожаловать в PHOENIX AGENCY!\n\n"
        "Мы рады, что ты заинтересовалась сотрудничеством с нами.\n\n"
        "Наш менеджер расскажет подробнее об условиях, "
        "ответит на твои вопросы и поможет сделать первые шаги.\n\n"
        "Будем рады видеть тебя в нашей команде! ✨"
    )

    keyboard = [[InlineKeyboardButton("💌 Связаться с менеджером", url=MANAGER_URL)]]
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не установлен")
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🔥 PHOENIX AGENCY BOT запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
