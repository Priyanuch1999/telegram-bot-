import asyncio
from datetime import datetime
import pytz
from telegram import Bot

TOKEN = "8813095334:AAHCdDkJbRxFvQPq539SWkw7-1q6jyvN3tc"
CHAT_ID = "-5264765115"

bot = Bot(token=TOKEN)
tz = pytz.timezone("Asia/Bangkok")

async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def scheduler():
    sent_morning = False
    sent_night = False
    
    while True:
        now = datetime.now(tz)
        hour = now.hour
        minute = now.minute

        if hour == 5 and minute == 0 and not sent_morning:
            await send_message("━━━━━━━━━━━━━━━\n🌅 GOOD MORNING | อรุณสวัสดิ์\n━━━━━━━━━━━━━━━\n🧠 No plan, No trade\n💰 Manage your risk first\n🎯 Trade the system, not emotions\n━━━━━━━━━━━━━━━\nGood Luck Today! 🍀")
            sent_morning = True
            sent_night = False

        elif hour == 0 and minute == 0 and not sent_night:
            await send_message("━━━━━━━━━━━━━━━\n🌙 GOOD NIGHT | ราตรีสวัสดิ์\n━━━━━━━━━━━━━━━\n📖 Review your trades today\n💤 Rest well, stay sharp tomorrow\n🎯 Markets will always be there\n━━━━━━━━━━━━━━━\nSee You Tomorrow! 💪")
            sent_night = True
            sent_morning = False

        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(scheduler())
