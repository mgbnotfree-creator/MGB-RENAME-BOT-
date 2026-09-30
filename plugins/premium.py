from pyrogram import Client, filters
from config import Config
from helper.database import digital_botz

@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium(bot, message):
    # सिर्फ एडमिन यह कमांड इस्तेमाल कर सकता है
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        # कमांड से यूज़र आईडी निकालना (जैसे: /addpremium 123456)
        user_id = int(message.text.split(" ", 1)[1])
        
        # डेटाबेस में प्रीमियम सेव करना
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": True}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": True}}, upsert=True)
            
        await message.reply_text(f"✅ **सफलतापूर्वक जोड़ दिया गया!**\n\nयूज़र `{user_id}` अब प्रीमियम मेम्बर है। उसकी डेली लिमिट हटा दी गई है।")
    except IndexError:
        await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/addpremium UserID`\nउदाहरण: `/addpremium 1234567890`")
    except Exception as e:
        await message.reply_text(f"⚠️ डेटाबेस एरर: {e}")

@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium(bot, message):
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        user_id = int(message.text.split(" ", 1)[1])
        
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": False}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": False}}, upsert=True)
            
        await message.reply_text(f"❌ **प्रीमियम हटा दिया गया!**\n\nयूज़र `{user_id}` अब फ्री मेम्बर है।")
    except IndexError:
        await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/removepremium UserID`")
    except Exception as e:
        await message.reply_text(f"⚠️ डेटाबेस एरर: {e}")
                   
