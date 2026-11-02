import os
import random
import string
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Thiếu TELEGRAM_TOKEN trong Environment Variables")

# Khởi tạo Application của Telegram
ptb_app = Application.builder().token(TOKEN).build()

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

# Đăng ký handler
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_password))

@app.route('/')
def home():
    return "Bot Webhook đang hoạt động tốt!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Hàm này nhận dữ liệu từ Telegram đẩy về"""
    update = Update.de_json(request.get_json(force=True), ptb_app.bot)
    
    # Dùng asyncio để chạy process_update trong Flask đồng bộ
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if not ptb_app._initialized:
        loop.run_until_complete(ptb_app.initialize())
        
    loop.run_until_complete(ptb_app.process_update(update))
    loop.close()
    
    return 'ok'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
