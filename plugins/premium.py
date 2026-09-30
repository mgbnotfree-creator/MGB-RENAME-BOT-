import time
import datetime
from pyrogram import Client, filters
from config import Config
from helper.database import digital_botz

@Client.on_message(filters.command("givepremium") & filters.private)
async def give_premium(bot, message):
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        args = message.text.split()
        if len(args) < 4:
            return await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/givepremium UserID Time Unit`\nउदाहरण:\n👉 `/givepremium 123456789 1 month`\n👉 `/givepremium 123456789 1 year`")
            
        user_id = int(args[1])
        time_val = int(args[2])
        time_unit = args[3].lower()
        
        # दिन, महीने और साल का कैलकुलेशन
        if time_unit in ["day", "days"]:
            seconds = time_val * 86400
        elif time_unit in ["month", "months"]:
            seconds = time_val * 30 * 86400
        elif time_unit in ["year", "years"]:
            seconds = time_val * 365 * 86400
        else:
            return await message.reply_text("⚠️ **गलत Unit!** सिर्फ day, month, या year लिखें।")
            
        expiry_time = time.time() + seconds
        expiry_date_str = datetime.datetime.fromtimestamp(expiry_time).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": True, "premium_expiry": expiry_time}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": True, "premium_expiry": expiry_time}}, upsert=True)
            
        await message.reply_text(f"✅ **प्रीमियम सफलतापूर्वक जोड़ दिया गया!**\n\n👤 **यूज़र:** `{user_id}`\n⏳ **प्लान:** {time_val} {time_unit}\n📅 **एक्सपायरी:** {expiry_date_str}\n\nइसकी 5 फाइलों की डेली लिमिट अब हटा दी गई है।")
    except Exception as e:
        await message.reply_text(f"⚠️ एरर: {e}")

@Client.on_message(filters.command("delpremium") & filters.private)
async def del_premium(bot, message):
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        user_id = int(message.text.split(" ", 1)[1])
        
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": False, "premium_expiry": 0}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": False, "premium_expiry": 0}}, upsert=True)
            
        await message.reply_text(f"❌ **प्रीमियम हटा दिया गया!**\n\nयूज़र `{user_id}` अब फ्री मेम्बर है। उस पर वापस लिमिट लग गई है।")
    except IndexError:
        await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/delpremium UserID`")
    except Exception as e:
        await message.reply_text(f"⚠️ एरर: {e}")
        
