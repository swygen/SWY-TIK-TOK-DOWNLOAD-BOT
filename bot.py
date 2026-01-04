import telebot
from telebot import types
import yt_dlp
import os
import time
from keep_alive import keep_alive

# 🔹 আপনার বট টোকেন দিন
API_TOKEN = '8526949244:AAGyCJ4HzQhs_hnwN_xSuOlM-8t8TM89-Ys'
bot = telebot.TeleBot(API_TOKEN)

# ইউজারদের লিংক এবং চ্যাট আইডি মনে রাখার জন্য
user_data = {}

# ==========================================
# 1. স্বাগতম মেসেজ ও মেইন মেনু (Reply Keyboard)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # মেইন মেনু বাটন
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_download = types.KeyboardButton("⬇️ ভিডিও ডাউনলোড")
    btn_dev = types.KeyboardButton("👨‍💻 ডেভেলপার ইনফো")
    markup.add(btn_download, btn_dev)

    user_name = message.from_user.first_name
    welcome_text = (
        f"আসসালামু আলাইকুম, {user_name}! 👋\n\n"
        "আমি **Swygen IT** এর অ্যাডভান্সড টিকটক ডাউনলোডার বট।\n"
        "নিচের বাটনগুলো ব্যবহার করে খুব সহজেই ওয়াটারমার্ক ছাড়া ভিডিও ডাউনলোড করতে পারবেন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 2. ডেভেলপার ইনফো হ্যান্ডলার
# ==========================================
@bot.message_handler(func=lambda message: message.text == "👨‍💻 ডেভেলপার ইনফো")
def dev_info(message):
    # ইনলাইন বাটন (ওয়েবসাইট লিংক)
    markup = types.InlineKeyboardMarkup()
    btn_site = types.InlineKeyboardButton("🌐 Visit Website", url="https://swygen.xyz")
    markup.add(btn_site)

    info_text = (
        "🛠 **ডেভেলপার তথ্য:**\n\n"
        "ডেভেলপার: **Ayman Hasan Shaan**\n"
        "ব্র্যান্ড: **Swygen IT**\n\n"
        "আমাদের সার্ভিস সম্পর্কে আরো জানতে ওয়েবসাইট ভিজিট করুন।"
    )
    bot.send_message(message.chat.id, info_text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 3. ডাউনলোড রিকোয়েস্ট হ্যান্ডলার
# ==========================================
@bot.message_handler(func=lambda message: message.text == "⬇️ ভিডিও ডাউনলোড")
def ask_for_link(message):
    msg = bot.send_message(message.chat.id, "🔗 দয়া করে আপনার **TikTok ভিডিওর লিংকটি** দিন:")
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    url = message.text
    chat_id = message.chat.id

    # লিংক ভ্যালিডেশন
    if "tiktok.com" not in url:
        bot.send_message(chat_id, "❌ এটি সঠিক TikTok লিংক নয়। দয়া করে আবার চেষ্টা করুন।")
        return

    # লিংকটি মেমোরিতে সেভ রাখা
    user_data[chat_id] = url

    # ফরম্যাট সিলেকশন বাটন (Inline Keyboard)
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_nowm = types.InlineKeyboardButton("🚫 Without Watermark", callback_data="type_nowm")
    btn_hd = types.InlineKeyboardButton("🌟 HD Quality", callback_data="type_hd")
    btn_mp3 = types.InlineKeyboardButton("🎵 Mp3 (Audio)", callback_data="type_mp3")
    markup.add(btn_nowm, btn_hd, btn_mp3)

    bot.send_message(chat_id, "📥 আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=markup)

# ==========================================
# 4. ফরম্যাট প্রসেসিং এবং ডাউনলোড (Callback Query)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_download_type(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user_data:
        bot.send_message(chat_id, "⚠️ সেশন এক্সপায়ার হয়ে গেছে। দয়া করে আবার লিংক দিন।")
        return

    url = user_data[chat_id]
    format_type = call.data
    
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="⏳ প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন।")

    try:
        file_name = f"video_{chat_id}"
        ydl_opts = {}

        # ফরম্যাট লজিক
        if format_type == "type_mp3":
            file_name += ".mp3"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': file_name,
            }
        elif format_type == "type_hd":
            file_name += ".mp4"
            ydl_opts = {
                'format': 'best', # HD Quality
                'outtmpl': file_name,
            }
        else: # Without Watermark (Default behavior of yt-dlp for TikTok)
            file_name += ".mp4"
            ydl_opts = {
                'format': 'best',
                'outtmpl': file_name,
            }

        # ডাউনলোড শুরু
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ফাইল পাঠানো
        with open(file_name, 'rb') as file:
            caption_text = "✅ ডাউনলোড সম্পন্ন!\n⚡ Powered by: Swygen IT"
            if format_type == "type_mp3":
                bot.send_audio(chat_id, file, caption=caption_text)
            else:
                bot.send_video(chat_id, file, caption=caption_text)

        # 🔹 ফিডব্যাক মেসেজ এবং লিংক বাটন
        markup = types.InlineKeyboardMarkup()
        btn_site = types.InlineKeyboardButton("🌐 Visit Swygen.xyz", url="https://swygen.xyz")
        markup.add(btn_site)
        
        user_name = call.from_user.first_name
        feedback_msg = f"প্রিয় {user_name}, সার্ভিসটি কী রকম লাগলো জানাতে ভুলবেন না! ❤️"
        
        bot.send_message(chat_id, feedback_msg, reply_markup=markup)

        # ক্লিনআপ (ফাইল ডিলিট)
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        bot.send_message(chat_id, "❌ দুঃখিত, ডাউনলোড করতে সমস্যা হয়েছে। লিংকটি পাবলিক কি না চেক করুন।")
        if os.path.exists(file_name):
            os.remove(file_name)

# Keep Alive এবং বট রান করা
keep_alive()
bot.polling(none_stop=True)
