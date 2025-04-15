import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI
import os
import openai

# Thiết lập log
logging.basicConfig(level=logging.INFO)

# API Key OpenAI và Telegram
TELEGRAM_TOKEN = '8139700391:AAG4UbMwrIhHbWRphlHgo-ewufXj3rDhAbw'
OPENAI_API_KEY = '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'
client = OpenAI(api_key=OPENAI_API_KEY)

# Vai trò mặc định
default_role = "Bạn là trợ lý AI hỗ trợ người dùng bằng tiếng Việt, trả lời ngắn gọn, dễ hiểu."
user_roles = {}  # Lưu vai trò theo chat_id

# Xử lý các lệnh đổi vai trò
async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cmd = update.message.text

    roles = {
        "/en_tutor": "Bạn là giáo viên tiếng Anh, sửa lỗi bài viết, giải thích ngữ pháp chi tiết.",
        "/pm_expert": "Bạn là chuyên gia quản lý dự án phần mềm, tư vấn về Hybrid, Waterfall, Agile, Scrum, estimation và quản lý nhóm kỹ thuật.",
        "/reset": default_role
    }

    if cmd in roles:
        user_roles[chat_id] = roles[cmd]
        await update.message.reply_text(f"✅ Đã chuyển vai trò bot sang: {cmd[1:]}")
    else:
        await update.message.reply_text("❌ Lệnh không hợp lệ.")

# Xử lý tin nhắn người dùng
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    print(f"📩 Người dùng nhắn: {user_message}")

    role = user_roles.get(chat_id, default_role)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": user_message},
            ]
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except openai.RateLimitError as e:
        print("❌ Lỗi quota:", e)
        await update.message.reply_text("🚫 Bot đã hết quota sử dụng API. Vui lòng nạp thêm để tiếp tục.")

    except Exception as e:
        print("❌ Lỗi khi gọi OpenAI:", e)
        await update.message.reply_text("⚠️ Xin lỗi! Bot đang gặp sự cố khi gọi ChatGPT.")

# Khởi động bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler(["en_tutor", "pm_expert", "reset"], set_role))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()