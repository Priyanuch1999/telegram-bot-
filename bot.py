import os
import asyncio
import threading
from datetime import datetime
import pytz
from flask import Flask, request
from telegram import Bot

# ===== ตั้งค่า (อ่านจาก Environment Variables ใน Railway) =====
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
# secret กันคนอื่นยิง webhook มั่ว (ตั้งคำอะไรก็ได เช่น "maestro123")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# ชื่อไฟลคลิป ที่อยู่ในโปรเจกต์เดียวกัน
VIDEO_FILE = "clip.mp4"
# เวลารอ (วินาที) ระหว่างสงคลิป กับส่งข้อความสัญญาณ
DELAY_SECONDS = 5

bot = Bot(token=TOKEN)
tz = pytz.timezone("Asia/Bangkok")
app = Flask(__name__)

# ===== สราง event loop ตัวเดียว รันค้างไว้ใน thread แยก =====
# (วิธีนี้แก้ปัญหา "Event loop is closed" ที่เกิดจากการเรียก asyncio.run ซ้ำ)
loop = asyncio.new_event_loop()


def _start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(target=_start_loop, daemon=True).start()


def run_async(coro):
    """ส่ง coroutine เข้าไปรันใน loop กลาง แล้วรอผลลัพธ"""
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


# ========== ส่วนที่ 1: สญญาณเทรด (คลิป + ข้อความ) ==========
async def send_signal(message_text):
    # 1) ส่งคลิป 4 วิ ก่อน
    with open(VIDEO_FILE, "rb") as video:
        await bot.send_video(chat_id=CHAT_ID, video=video)
    # 2) รอ 5 วินาที
    await asyncio.sleep(DELAY_SECONDS)
    # 3) ส่งข้อความสัญญาณเทรด
    await bot.send_message(chat_id=CHAT_ID, text=message_text)


@app.route("/webhook", methods=["POST"])
def webhook():
    if WEBHOOK_SECRET:
        if request.headers.get("X-Secret") != WEBHOOK_SECRET:
            return "unauthorized", 401
    message_text = request.get_data(as_text=True)
    if not message_text.strip():
        return "empty", 400
    run_async(send_signal(message_text))
    return "ok", 200


@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


# ========== ส่วนที่ 2: ทักทายเช้า/คน อัตโนมัติ ==========
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
    # สั่งให้ scheduler (ทักทาย) ทำงานใน loop กลาง
    asyncio.run_coroutine_threadsafe(scheduler(), loop)
    # รัน Flask (รับ webhook สัญญาณเทรด)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
