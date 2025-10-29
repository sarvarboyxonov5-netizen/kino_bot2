import telebot
from telebot import types

BOT_TOKEN = "8474990891:AAEH1bGRI5WEtgqdo1yQUGObAJS1RUMLI-k"
ADMIN_ID = 8297713790
KANALLAR = [("@Kinomaniya_fast", "https://t.me/Kinomaniya_fast")]

bot = telebot.TeleBot(BOT_TOKEN)
kino_baza = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for kanal_name, kanal_link in KANALLAR:
        markup.add(types.InlineKeyboardButton("📢 A’zo bo‘lish", url=kanal_link))
    markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_subs"))
    bot.send_message(message.chat.id,
        "🎬 Botdan foydalanish uchun quyidagi kanalga a’zo bo‘ling.\n\n"
        "A’zo bo‘lgach, pastdagi '✅ Tasdiqlash' tugmasini bosing 👇",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    user_id = call.from_user.id
    for kanal_name, _ in KANALLAR:
        status = bot.get_chat_member(kanal_name, user_id).status
        if status not in ["member", "administrator", "creator"]:
            bot.answer_callback_query(call.id, "❌ Siz hali kanalga a’zo bo‘lmadingiz!")
            return
    bot.answer_callback_query(call.id, "✅ A’zolik tasdiqlandi!")
    bot.send_message(call.message.chat.id, "Assalomu alaykum! 🎬 Kino kodini yuboring:")

@bot.message_handler(commands=['upload'])
def upload_kino(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    bot.reply_to(message, "🎥 Kino videosini yuboring:")
    bot.register_next_step_handler(message, save_video)

def save_video(message):
    if not message.video:
        bot.reply_to(message, "❗ Bu video emas, qayta urinib ko‘ring.")
        return
    video_id = message.video.file_id
    bot.reply_to(message, "🔢 Endi ushbu kinoga kod kiriting (masalan: 4):")
    bot.register_next_step_handler(message, save_code, video_id)

def save_code(message, video_id):
    kod = message.text.strip()
    kino_baza[kod] = video_id
    bot.reply_to(message, f"✅ Kino muvaffaqiyatli yuklandi!\nKod: `{kod}`", parse_mode="Markdown")

@bot.message_handler(commands=['delete'])
def delete_kino(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    bot.reply_to(message, "🗑 O‘chirmoqchi bo‘lgan kino kodini kiriting:")
    bot.register_next_step_handler(message, remove_video)

def remove_video(message):
    kod = message.text.strip()
    if kod in kino_baza:
        del kino_baza[kod]
        bot.reply_to(message, f"✅ Kino kodi `{kod}` muvaffaqiyatli o‘chirildi!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Bunday kod topilmadi.")

@bot.message_handler(func=lambda m: True)
def send_kino(message):
    kod = message.text.strip()
    if kod in kino_baza:
        video_id = kino_baza[kod]
        bot.send_video(message.chat.id, video_id, caption=f"🎬 Siz so‘ragan kino (Kod: {kod})")
    elif message.text not in ["/upload", "/delete", "/start"]:
        bot.send_message(message.chat.id, "❌ Bunday kod topilmadi.\nIltimos, kodni to‘g‘ri kiriting.")

print("🤖 Bot ishga tushdi...")
bot.polling(none_stop=True)
