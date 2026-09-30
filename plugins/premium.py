from pyrogram import Client, filters
from config import Config
from helper.database import digital_botz

@Client.on_message(filters.command("givepremium") & filters.private)
async def give_premium(bot, message):
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        user_id = int(message.text.split(" ", 1)[1])
        
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": True}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": True}}, upsert=True)
            
        await message.reply_text(f"✅ **सफलतापूर्वक जोड़ दिया गया!**\n\nयूज़र `{user_id}` अब VIP मेम्बर है। उसकी 5 फाइलों की डेली लिमिट हमेशा के लिए हटा दी गई है।")
    except IndexError:
        await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/givepremium UserID`\nउदाहरण: `/givepremium 1234567890`")
    except Exception as e:
        await message.reply_text(f"⚠️ डेटाबेस एरर: {e}")

@Client.on_message(filters.command("delpremium") & filters.private)
async def del_premium(bot, message):
    if message.from_user.id != Config.ADMIN:
        return
    
    try:
        user_id = int(message.text.split(" ", 1)[1])
        
        try:
            await digital_botz.col.update_one({"_id": user_id}, {"$set": {"is_premium": False}}, upsert=True)
        except AttributeError:
            await digital_botz.db.users.update_one({"_id": user_id}, {"$set": {"is_premium": False}}, upsert=True)
            
        await message.reply_text(f"❌ **प्रीमियम हटा दिया गया!**\n\nयूज़र `{user_id}` अब फ्री मेम्बर है। उस पर वापस लिमिट लग गई है।")
    except IndexError:
        await message.reply_text("⚠️ **गलत तरीका!**\n\nऐसे इस्तेमाल करें: `/delpremium UserID`")
    except Exception as e:
        await message.reply_text(f"⚠️ डेटाबेस एरर: {e}")
        
