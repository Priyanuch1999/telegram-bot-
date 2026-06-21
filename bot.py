import os
import asyncio
import threading
from datetime import datetime
import pytz
from flask import Flask, request
from telegram import Bot
from telegram.request import HTTPXRequest

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

VIDEO_FILE = "clip.mp4.MP4"
DELAY_SECONDS = 5

bot = Bot(token=TOKEN, request=HTTPXRequest(read_timeout=60, connect_timeout=60))

tz = pytz.timezone("Asia/Bangkok")
app = Flask(__name__)

loop = asyncio.new_event_loop()

def _start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=_start_loop, daemon=True).start()

def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

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
    raw = request.get_data(as_text=True)
    try:
        import json
        data = json.loads(raw)
        message_text = data.get("text", raw)
    except:
        message_text = raw
    if not message_text.strip():
        return "empty", 400
    run_async(send_signal(message_text))
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200

async def scheduler():
    sent_morning = False
    sent_night = False
    while True:
        now = datetime.now(tz)
        hour = now.hour
        minute = now.minute
        if hour == 5 and minute == 0 and not sent_morning:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="——————————\n🌅 GOOD MORNING | อรุณสวัสดิ์\n——————————\n🧠 No plan, No trade\n💰 Manage your risk first\n🎯 Trade the system, not emotions\n——————————\nGood Luck Today! 🍀",
            )
            sent_morning = True
            sent_night = False
        elif hour == 0 and minute == 0 and not sent_night:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="——————————\n🌙 GOOD NIGHT | ราตรีสวัสดิ์\n——————————\n📖 Review your trades\n——————————",
            )
            sent_night = True
            sent_morning = False
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run_coroutine_threadsafe(scheduler(), loop)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
