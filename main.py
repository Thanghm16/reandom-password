import random
import string
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8855431557:AAGgkiZNCx8wLYPUVhGP1CMbu6vTGCK-cpo"

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
    if not update.message or not update.message.text:
        return
    account_name = update.message.text
    new_password = generate_password()
    reply_message = f"Tài khoản: {account_name}\nMật khẩu: <code>{new_password}</code>"
    await update.message.reply_text(reply_message, parse_mode='HTML')

ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_password))

# Hàm này giúp quản lý việc bật/tắt bot an toàn cùng với server
@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb_app.initialize()
    await ptb_app.start()
    yield
    await ptb_app.stop()
    await ptb_app.shutdown()

app = FastAPI(lifespan=lifespan)

# Đường dẫn này dành cho UptimeRobot gõ cửa kiểm tra
@app.get("/")
async def home():
    return "Bot đang thức và hoạt động mượt mà!"

# Đường dẫn này dành riêng cho Telegram gửi tin nhắn tới
@app.post(f"/{TOKEN}")
async def webhook_telegram(req: Request):
    data = await req.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"status": "ok"}
