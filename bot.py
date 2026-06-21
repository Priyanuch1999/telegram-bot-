import os
import asyncio
from flask import Flask, request
from telegram import Bot

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

VIDEO_FILE = "clip.mp4"
DELAY_SECONDS = 5

bot = Bot(token=TOKEN)
app = Flask(__name__)


async def send_signal(message_text):
    with open(VIDEO_FILE, "rb") as video:
        await bot.send_video(chat_id=CHAT_ID, video=video)
    await asyncio.sleep(DELAY_SECONDS)
    await bot.send_message(chat_id=CHAT_ID, text=message_text)


@app.route("/webhook", methods=["POST"])
def webhook():
    if WEBHOOK_SECRET:
        if request.headers.get("X-Secret") != WEBHOOK_SECRET:
            return "unauthorized", 401
    message_text = request.get_data(as_text=True)
    if not message_text.strip():
        return "empty", 400
    asyncio.run(send_signal(message_text))
    return "ok", 200


@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
