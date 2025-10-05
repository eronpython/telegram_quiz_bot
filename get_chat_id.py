import telebot

TOKEN = "8359356550:AAFgGm9wxkWddOtBHdj-b44Vd0EjxHSkAG8"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'id'])
def send_id(message):
    bot.reply_to(message, f"👋 Hello, {message.from_user.first_name}!\nYour user ID: {message.chat.id}")

print("✅ Send /start or /id to your bot on Telegram")
bot.infinity_polling()
