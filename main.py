import os
import random
import string
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang sống!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

def generate_password(length=12):
    first_char = random.choice(string.ascii_uppercase)
    required_chars = [random.choice(string.digits), '@']
    remaining_length = length - 1 - len(required_chars)
    random_chars = [random.choice(string.ascii_lowercase + string.digits) for _ in range(remaining_length)]
    
    tail_chars = required_chars + random_chars
    random.shuffle(tail_chars)
    return first_char + "".join(tail_chars)

async def reply_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    account_name = update.message.text
    new_password = generate_password()
    reply_message = f"Tài khoản: {account_name}\nMật khẩu: <code>{new_password}</code>"
    await update.message.reply_text(reply_message, parse_mode='HTML')

def main():
    # Lấy token từ Environment Variables
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    # Báo lỗi nếu quên chưa thêm biến môi trường
    if not TOKEN:
        raise ValueError("Chưa tìm thấy biến môi trường TELEGRAM_TOKEN. Vui lòng thêm vào Render!")
        
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_password))
    
    print("Khởi động bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web)
    web_thread.start()
    main()
