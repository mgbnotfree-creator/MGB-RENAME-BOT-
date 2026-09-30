from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle, MessageMediaType, ParseMode
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import digital_botz
from helper.ffmpeg import change_metadata, get_duration
from config import Config
import os, time, asyncio
from html import escape
import logging

UPLOAD_TEXT = """Uploading Started...."""
DOWNLOAD_TEXT = """Download Started..."""

logger = logging.getLogger(__name__)

# ---> ORIGINAL APP CLIENT - DO NOT REMOVE <---
app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION, parse_mode=ParseMode.HTML)


async def upload_files(bot, sender_id, upload_type, file_path, ph_path, caption, duration, rkn_processing):
    """
    Unified function to upload files based on type
    """
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        if upload_type == "document":
            filw = await bot.send_document(
                sender_id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        elif upload_type == "video":
            filw = await bot.send_video(
                sender_id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        elif upload_type == "audio":
            filw = await bot.send_audio(
                sender_id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        else:
            return None, f"Unknown upload type: {upload_type}"
        return filw, None
    except Exception as e:
        return None, str(e)


# --- Simplified Direct Auto Rename ---
@app.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def auto_rename_start(client, message):
    user_id = message.from_user.id if message.from_user else message.chat.id
    file = getattr(message, message.media.value, None)
    
    if not file:
        return

    # Fetch original filename or audio title
    filename = getattr(file, "file_name", None)
    if not filename:
        if message.media == MessageMediaType.AUDIO:
            title = getattr(file, "title", None)
            if title:
                filename = f"{title}.m4a"
            else:
                filename = f"audio_{int(time.time())}.m4a"
        elif message.media == MessageMediaType.VIDEO:
            filename = f"video_{int(time.time())}.mp4"
        else:
            filename = f"file_{int(time.time())}.mkv"

    # Direct process - no asking
    rkn_processing = await message.reply_text("<code>Added to queue... Processing...</code>", quote=True)
    
    user_data = await digital_botz.get_user_data(user_id)
    if not user_data:
        user_data = {}
    
    try:
        prefix = user_data.get('prefix', None)
        suffix = user_data.get('suffix', None)
        new_filename = await add_prefix_suffix(filename, prefix, suffix)
    except Exception as e:
        return await rkn_processing.edit(f"⚠️ Error setting Prefix/Suffix: {escape(str(e))}")

    # Determine Upload Type
    if message.media == MessageMediaType.VIDEO:
        upload_type = "video"
    elif message.media == MessageMediaType.AUDIO:
        upload_type = "audio"
    else:
        upload_type = "document"

    # Creating Directory
    os.makedirs("Metadata", exist_ok=True)
    os.makedirs("Renames", exist_ok=True)

    file_path = f"Renames/{new_filename}"
    metadata_path = f"Metadata/{new_filename}"

    await rkn_processing.edit("<code>Downloading...</code>")
    
    # Download File
    try:            
        dl_path = await client.download_media(message=message, file_name=file_path, progress=progress_for_pyrogram, progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time()))                    
    except Exception as e:
        return await rkn_processing.edit(f"Download Error: {escape(str(e))}")

    # Process Metadata
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
        pass
    
    await rkn_processing.edit("<code>Uploading...</code>")
    final_file_path = metadata_path if (metadata_mode and os.path.exists(metadata_path)) else file_path
    
    duration = await get_duration(final_file_path)
    ph_path = None
    
    # Caption
    c_caption = user_data.get('caption', None)
    c_thumb = user_data.get('file_id', None)
    
    if c_caption:
         try:
             caption = c_caption.format(filename=escape(str(new_filename)), filesize=escape(humanbytes(file.file_size)), duration=escape(str(convert(duration))))
         except Exception:
             caption = f"<b>{escape(str(new_filename))}</b>"             
    else:
         caption = f"<b>{escape(str(new_filename))}</b>\n\n<b>User:</b> {escape(str(message.from_user.first_name))}\n<b>User ID:</b> <code>{user_id}</code>"
         
    # Thumbnail
    if (file.thumbs or c_thumb):
         try:
             if c_thumb:
                 ph_path = await client.download_media(c_thumb) 
             elif file.thumbs:
                 ph_path = await client.download_media(file.thumbs[0].file_id)
             
             if ph_path and os.path.exists(ph_path):
                 with Image.open(ph_path) as img:
                     img.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS).save(ph_path, "JPEG")
         except Exception as e:
             logger.exception("Thumbnail error: %s", e)
             ph_path = None

    # Upload File
    filw, error = await upload_files(
        client, message.chat.id, upload_type, final_file_path, 
        ph_path, caption, duration, rkn_processing
    )
    
    if error:
        await remove_path(ph_path, file_path, dl_path, metadata_path)
        return await rkn_processing.edit(f"Upload Error: {escape(str(error))}")

    if Config.BIN_CHANNEL:
        try:
            await client.copy_message(chat_id=Config.BIN_CHANNEL, from_chat_id=filw.chat.id, message_id=filw.id)
        except Exception:
            pass
            
    await remove_path(ph_path, file_path, dl_path, metadata_path)
    await rkn_processing.delete()

