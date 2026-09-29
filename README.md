<div align="center">

<img src="https://bannerrender.vercel.app/api?type=waving&height=300&color=gradient&text=𝗥𝗲𝗻𝗮𝗺𝗲%20𝗕𝗼𝘁&fontAlignY=35&fontSize=80&desc=𝗚𝗶𝘃𝗶𝗻𝗴%20𝗬𝗼𝘂𝗿%20𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺%20𝗙𝗶𝗹𝗲𝘀%20𝗮%20𝗠𝗮𝗸𝗲𝗼𝘃𝗲𝗿&descAlignY=60"/>

<p align="center">
A powerful Telegram bot designed to effortlessly rename and customize files with custom thumbnails, metadata, and captions.
</p>

</div>

---

## ✨ Key Features

- 📦 **4GB File Support** (with STRING_SESSION)
- 🖼️ **Custom Thumbnails & Metadata** configuration
- 🔄 **File Conversion** (Video to Document and vice versa)
- ⚡ **Fast & Unlimited Renaming**
- 🔐 **Force Subscribe** and Broadcast System
- 🚀 **Multi-Platform Support** (Heroku, Render, Koyeb, etc.)

---

## ⚙️ Required Variables

To deploy the bot, you will primarily need these environment variables:

- `API_ID` & `API_HASH` (From Telegram API)
- `BOT_TOKEN` (From BotFather)
- `DB_URL` (MongoDB Database URL)
- `ADMIN` (Your Telegram User ID)
- `STRING_SESSION` (Optional - for 4GB file support)

---

## 🤖 Main Commands

- `/start` - Check if the bot is alive.
- `/viewthumb` / `/delthumb` - View or delete the current thumbnail.
- `/setcaption` / `/delcaption` - Set or delete a custom caption.
- `/metadata` - Toggle custom metadata on/off.
- `/status` - View bot statistics (Admin only).

---

## 🚀 Deployment

### Run Locally

```bash
# 1. Install requirements
pip install -r requirements.txt

# 2. Set your environment variables
export API_ID=... API_HASH=... BOT_TOKEN=... ADMIN=... DB_URL=...

# 3. Start the bot
python bot.py

> 📺 Deployment Tutorial: Watch the YouTube Playlist for step-by-step setup guides.
> 
📄 License
This project is under the Apache 2.0 License. It is intended for educational purposes only.
🙌 Credits
This project is based on the original work of the following developers:
 * DigitalBotz
 * Bisu Ghalan
👤 Contact
For any help, support, or inquiries, you can reach out here:
 * Telegram: @MGB_NOT_FREE

