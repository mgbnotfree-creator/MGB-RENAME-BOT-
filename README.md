<div align="center">

<img src="https://bannerrender.vercel.app/api?type=waving&height=300&color=gradient&text=𝗥𝗲𝗻𝗮𝗺𝗲%20𝗕𝗼𝘁&fontAlignY=35&fontSize=80&desc=𝗚𝗶𝘃𝗶𝗻𝗴%20𝗬𝗼𝘂𝗿%20𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺%20𝗙𝗶𝗹𝗲𝘀%20𝗮%20𝗠𝗮𝗸𝗲𝗼𝘃𝗲𝗿&descAlignY=60"/>

<p align="center">
एक शक्तिशाली टेलीग्राम बॉट जिसे कस्टम थंबनेल, मेटाडेटा और कैप्शन के साथ फ़ाइलों को आसानी से रीनेम और कस्टमाइज़ करने के लिए डिज़ाइन किया गया है।
</p>

</div>

---

## ✨ मुख्य विशेषताएं (Key Features)

- 📦 **4GB फ़ाइल सपोर्ट** (STRING_SESSION के साथ)
- 🖼️ **कस्टम थंबनेल और मेटाडेटा** सेट करने की सुविधा
- 🔄 **फ़ाइल रूपांतरण** (वीडियो से दस्तावेज़ और इसके विपरीत)
- ⚡ **तेज़ और असीमित रीनेमिंग**
- 🔐 **फोर्स सब्सक्राइब (Force Subscribe)** और ब्रॉडकास्ट सिस्टम
- 🚀 **मल्टी-प्लेटफ़ॉर्म सपोर्ट** (Heroku, Render, Koyeb आदि)

---

## ⚙️ आवश्यक कॉन्फ़िगरेशन (Required Variables)

बॉट को डिप्लॉय करने के लिए आपको मुख्य रूप से इन वेरिएबल्स की आवश्यकता होगी:

- `API_ID` और `API_HASH` (Telegram API)
- `BOT_TOKEN` (BotFather से)
- `DB_URL` (MongoDB डेटाबेस URL)
- `ADMIN` (आपका टेलीग्राम User ID)
- `STRING_SESSION` (4GB सपोर्ट के लिए - वैकल्पिक)

---

## 🤖 मुख्य कमांड्स (Main Commands)

- `/start` - बॉट को चेक करें।
- `/viewthumb` / `/delthumb` - थंबनेल देखें या हटाएं।
- `/setcaption` / `/delcaption` - कस्टम कैप्शन सेट या डिलीट करें।
- `/metadata` - कस्टम मेटाडेटा चालू/बंद करें।
- `/status` - बॉट के आंकड़े (स्टैट्स) देखें (केवल एडमिन)।

---

## 🚀 डिप्लॉयमेंट (Deployment)

### लोकल सिस्टम पर चलाएं (Run Locally)

```bash
# 1. रिक्वायरमेंट्स इंस्टॉल करें
pip install -r requirements.txt

# 2. अपने वेरिएबल्स सेट करें (Environment Variables)
export API_ID=... API_HASH=... BOT_TOKEN=... ADMIN=... DB_URL=...

# 3. बॉट स्टार्ट करें
python bot.py
