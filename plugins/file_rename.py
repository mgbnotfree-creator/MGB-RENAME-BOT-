from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle, MessageMediaType, ParseMode
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyParameters
from PIL import Image
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import digital_botz
from helper.ffmpeg import change_metadata, get_duration
from config import Config, rkn
import os, time, asyncio
from html import escape
import logging

UPLOAD_TEXT = """Uploading Started...."""
DOWNLOAD_TEXT = """Download Started..."""

logger = logging.getLogger(__name__)

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION, parse_mode=ParseMode.HTML)

# --- Direct Auto Rename Logic ---
@Client.on_message(filters.private & (filters.audio | filters.document | filters.video))
async def auto_rename_start(client, message):
    user_id = message.from_user.id
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanbytes(file.file_size)
    
    if not filename:
        filename = f"unknown_{int(time.time())}.mkv"
        
    # Check limits first
    if client.premium and client.uploadlimit:
        user_data = await digital_botz.reset_uploadlimit_access(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit) - int(used)
        if remain < int(file.file_size):
            used_percentage = int(used) / int(limit) * 100
            return await message.reply_text(f"{used_percentage:.2f}% Of Daily Upload Limit {humanbytes(limit)}.\n\n Media Size: {filesize}\n Your Used Daily Limit {humanbytes(used)}\n\nYou have only <b>{humanbytes(remain)}</b> Data.\nPlease, Buy Premium Plan s.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 Uᴘɢʀᴀᴅᴇ", callback_data="plans", style=ButtonStyle.SUCCESS)]]))
            
    if not client.premium and file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("If you want to rename 4GB+ files then you will have to buy premium. /plans")
        
    if client.premium and not Config.STRING_SESSION and file.file_size > 2000 * 1024 * 1024:
         return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ+")

    # Prepare for processing
    rkn_processing = await message.reply_text("<code>Added to queue... Processing...</code>", quote=True)
    
    user_data = await digital_botz.get_user_data(user_id)
    
    # Process Name with Prefix/Suffix
    try:
        prefix = user_data.get('prefix', None)
        suffix = user_data.get('suffix', None)
        new_filename = await add_prefix_suffix(filename, prefix, suffix)
    except Exception as e:
        return await rkn_processing.edit(f"⚠️ Something went wrong setting Prefix/Suffix\nError: {escape(str(e))}")

    # Determine Upload Type
    if message.media == MessageMediaType.VIDEO:
        upload_type = "video"
    elif message.media == MessageMediaType.AUDIO:
        upload_type = "audio"
    else:
        upload_type = "document"

    # Creating Directory for Metadata
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
    if not os.path.isdir("Renames"):
        os.mkdir("Renames")

    file_path = f"Renames/{new_filename}"
    metadata_path = f"Metadata/{new_filename}"

    await rkn_processing.edit("<code>Downloading...</code>")
    
    # Update Used Limit
    if client.premium and client.uploadlimit:
        used = user_data.get('used_limit', 0)        
        total_used = int(used) + int(file.file_size)
        await digital_botz.set_used_limit(user_id, total_used)

    # Download File
    try:            
        dl_path = await client.download_media(message=message, file_name=file_path, progress=progress_for_pyrogram, progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time()))                    
    except Exception as e:
        if client.premium and client.uploadlimit:
            used_remove = int(used) - int(file.file_size)
            await digital_botz.set_used_limit(user_id, used_remove)
        return await rkn_processing.edit(f"Download Error: {escape(str(e))}")

    # Process Metadata
    metadata_mode = await digital_botz.get_metadata_mode(user_id)
    if metadata_mode:        
        metadata = await digital_botz.get_metadata_code(user_id)
        if metadata:
            await rkn_processing.edit("<b>Adding Metadata...</b>")            
            if await change_metadata(dl_path, metadata_path, metadata):            
                logger.info("Metadata added")
            else:
                metadata_mode = False
        else:
            metadata_mode = False
    
    await rkn_processing.edit("<code>Uploading...</code>")
    duration = await get_duration(file_path if os.path.exists(file_path) else dl_path)
    ph_path = None
    
    # Caption and Thumbnail Logic
    c_caption = user_data.get('caption', None)
    c_thumb = user_data.get('file_id', None)
    
    if c_caption:
         try:
             caption = c_caption.format(filename=escape(str(new_filename)), filesize=escape(humanbytes(file.file_size)), duration=escape(str(convert(duration))))
         except Exception as e:
             if client.premium and client.uploadlimit:
                 used_remove = int(used) - int(file.file_size)
                 await digital_botz.set_used_limit(user_id, used_remove)
             return await rkn_processing.edit(text=f"Caption Error: ({escape(str(e))})")             
    else:
         caption = f"<b>{escape(str(new_filename))}</b>\n\n<b>User:</b> {escape(str(message.from_user.first_name))}\n<b>User ID:</b> <code>{user_id}</code>"
         
    if (file.thumbs or c_thumb):
         try:
             if c_thumb:
                 ph_path = await client.download_media(c_thumb) 
             else:
                 ph_path = await client.download_media(file.thumbs[0].file_id)
             
             if ph_path and os.path.exists(ph_path):
                 with Image.open(ph_path) as img:
                     img.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS).save(ph_path, "JPEG")
         except Exception as e:
             logger.exception("Error processing thumbnail: %s", e)
             ph_path = None

    final_file_path = metadata_path if metadata_mode and os.path.exists(metadata_path) else file_path

    # Upload File
    filw, error = await upload_files(
        client, message.chat.id, upload_type, final_file_path, 
        ph_path, caption, duration, rkn_processing
    )
    
    if error:
        if client.premium and client.uploadlimit:
            used_remove = int(used) - int(file.file_size)
            await digital_botz.set_used_limit(user_id, used_remove)
        await remove_path(ph_path, file_path, dl_path, metadata_path)
        return await rkn_processing.edit(f"Upload Error: {escape(str(error))}")

    # Forward to Bin Channel if Configured
    if Config.BIN_CHANNEL:
        try:
            await client.copy_message(chat_id=Config.BIN_CHANNEL, from_chat_id=filw.chat.id, message_id=filw.id)
        except Exception:
            logger.exception("bin channel copy failed")
            
    await remove_path(ph_path, file_path, dl_path, metadata_path)
    return await rkn_processing.edit("<b>Upload Complete!</b>")

# Keep the upload_files helper function exactly as it was
async def upload_files(bot, sender_id, upload_type, file_path, ph_path, caption, duration, rkn_processing):
    """
    Unified function to upload files based on type
    - Supports both 2GB and 4GB files
    - Uses same function for all file sizes
    - Handles document, video, and audio files
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        # Upload document files (2GB & 4GB)
        if upload_type == "document":
            filw = await bot.send_document(
                sender_id,
                document=file_path,
                thumb=ph_path,
                caption=caption,
                progress=progress_for_pyrogram,
                progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        # Upload video files (2GB & 4GB)  
        elif upload_type == "video":
            filw = await bot.send_video(
                sender_id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        # Upload audio files (2GB & 4GB)
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
        # Return uploaded file object
        return filw, None
    except Exception as e:
        # Return error if upload fails
        return None, str(e)
            
