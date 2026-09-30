from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType, ParseMode
from PIL import Image
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import digital_botz
from helper.ffmpeg import change_metadata, get_duration
from config import Config
import os, time, asyncio
from html import escape
import logging
from datetime import date

UPLOAD_TEXT = """Uploading Started...."""
DOWNLOAD_TEXT = """Download Started..."""

logger = logging.getLogger(__name__)

# ---> 4GB Session Client <---
app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION, parse_mode=ParseMode.HTML)

# ==========================================
# 🛑 DAILY LIMIT SETTINGS 🛑
# ==========================================
DAILY_LIMIT = 10  
user_usage = {}   
# ==========================================

async def upload_files(bot, sender_id, upload_type, file_path, ph_path, caption, duration, rkn_processing):
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        if upload_type == "document":
            filw = await bot.send_document(
                sender_id, document=file_path, thumb=ph_path, caption=caption,
                progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        elif upload_type == "video":
            filw = await bot.send_video(
                sender_id, video=file_path, caption=caption, thumb=ph_path, duration=duration,
                progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        elif upload_type == "audio":
            filw = await bot.send_audio(
                sender_id, audio=file_path, caption=caption, thumb=ph_path, duration=duration,
                progress=progress_for_pyrogram, progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        else:
            return None, f"Unknown upload type: {upload_type}"
        return filw, None
    except Exception as e:
        return None, str(e)


@Client.on_message(filters.private & (filters.audio | filters.document | filters.video), group=1)
async def auto_rename_start(bot, message):
    try:
        user_id = message.from_user.id if message.from_user else message.chat.id
        
        # 1. सबसे पहले यूज़र का डेटा निकालें ताकि पता चले कि वो प्रीमियम है या नहीं
        user_data = await digital_botz.get_user_data(user_id)
        if not user_data:
            user_data = {}
            
        is_premium = user_data.get('is_premium', False)
        
        # --- DAILY LIMIT CHECK ---
        today = date.today().isoformat()
        
        if user_id not in user_usage or user_usage[user_id]['date'] != today:
            user_usage[user_id] = {'date': today, 'count': 0}
            
        # अगर यूज़र एडमिन (Admin) या प्रीमियम (Premium) नहीं है, तभी लिमिट लगेगी
        if user_usage[user_id]['count'] >= DAILY_LIMIT and user_id != Config.ADMIN and not is_premium:
            await message.reply_text(f"⚠️ **आपकी आज की लिमिट खत्म हो गई है!**\n\nआप 1 दिन में सिर्फ {DAILY_LIMIT} फाइलें ही रीनेम कर सकते हैं।\n\n👑 **अनलिमिटेड रीनेम के लिए प्रीमियम खरीदें!** (संपर्क करें: Admin)")
            return
            
        user_usage[user_id]['count'] += 1
        # -------------------------

        file = None
        if message.document:
            file = message.document
            upload_type = "document"
            default_ext = "mkv"
        elif message.video:
            file = message.video
            upload_type = "video"
            default_ext = "mp4"
        elif message.audio:
            file = message.audio
            upload_type = "audio"
            default_ext = "m4a"
        else:
            return 

        filename = "Unknown_File"
        if hasattr(file, 'file_name') and file.file_name:
            filename = file.file_name
        elif hasattr(file, 'title') and file.title:
            filename = f"{file.title}.{default_ext}"
        else:
            filename = f"Downloaded_Media_{int(time.time())}.{default_ext}"

        filename = filename.replace("/", "_").replace("\\", "_")

        rkn_processing = await message.reply_text("<code>Added to queue... Processing...</code>")
        
        try:
            prefix = user_data.get('prefix', None)
            suffix = user_data.get('suffix', None)
            new_filename = await add_prefix_suffix(filename, prefix, suffix)
        except Exception as e:
            logger.error(f"Prefix/Suffix Error: {e}")
            new_filename = filename 

        os.makedirs("Metadata", exist_ok=True)
        os.makedirs("Renames", exist_ok=True)

        file_path = f"Renames/{new_filename}"
        metadata_path = f"Metadata/{new_filename}"

        await rkn_processing.edit("<code>Downloading...</code>")
        
        try:            
            dl_path = await bot.download_media(message=message, file_name=file_path, progress=progress_for_pyrogram, progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time()))                    
        except Exception as e:
            return await rkn_processing.edit(f"Download Error: {escape(str(e))}")

        metadata_mode = False
        try:
            metadata_mode = await digital_botz.get_metadata_mode(user_id)
            if metadata_mode:        
                metadata = await digital_botz.get_metadata_code(user_id)
                if metadata:
                    await rkn_processing.edit("<b>Adding Metadata...</b>")            
                    if not await change_metadata(dl_path, metadata_path, metadata):            
                        metadata_mode = False
                else:
                    metadata_mode = False
        except Exception:
            metadata_mode = False
        
        await rkn_processing.edit("<code>Uploading...</code>")
        final_file_path = metadata_path if (metadata_mode and os.path.exists(metadata_path)) else file_path
        
        duration = await get_duration(final_file_path)
        ph_path = None
        
        c_caption = user_data.get('caption', None)
        c_thumb = user_data.get('file_id', None)
        
        if c_caption:
             try:
                 caption = c_caption.format(filename=escape(str(new_filename)), filesize=escape(humanbytes(file.file_size)), duration=escape(str(convert(duration))))
             except Exception:
                 caption = f"<b>{escape(str(new_filename))}</b>"             
        else:
             caption = f"<b>{escape(str(new_filename))}</b>\n\n<b>User:</b> {escape(str(message.from_user.first_name))}\n<b>User ID:</b> <code>{user_id}</code>"
             
        if (hasattr(file, 'thumbs') and file.thumbs) or c_thumb:
             try:
                 if c_thumb:
                     ph_path = await bot.download_media(c_thumb) 
                 elif file.thumbs:
                     ph_path = await bot.download_media(file.thumbs[0].file_id)
                 
                 if ph_path and os.path.exists(ph_path):
                     with Image.open(ph_path) as img:
                         img.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS).save(ph_path, "JPEG")
             except Exception as e:
                 logger.exception("Thumbnail error: %s", e)
                 ph_path = None

        filw, error = await upload_files(
            bot, message.chat.id, upload_type, final_file_path, 
            ph_path, caption, duration, rkn_processing
        )
        
        if error:
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await rkn_processing.edit(f"Upload Error: {escape(str(error))}")

        if Config.BIN_CHANNEL:
            try:
                await bot.copy_message(chat_id=Config.BIN_CHANNEL, from_chat_id=filw.chat.id, message_id=filw.id)
            except Exception:
                pass
                
        await remove_path(ph_path, file_path, dl_path, metadata_path)
        await rkn_processing.delete()

    except Exception as e:
        logger.error(f"Critical error in auto_rename: {e}")
        try:
            await message.reply_text(f"⚠️ Error processing file: {e}")
        except:
            pass
        
