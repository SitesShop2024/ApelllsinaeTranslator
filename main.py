import telebot
import threading
from deep_translator import GoogleTranslator, single_detection
from flask import Flask

app = Flask(__name__)

TOKEN = '8446885622:AAGp8wDzuLzAkq3hOALDK1v8TMvBmRG0plM'
bot = telebot.TeleBot(TOKEN)


LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)
LANG_CODES = {v.lower(): k for k, v in LANGUAGES.items()}  # {'english': 'en', 'английский': 'en'}


user_langs = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Я переводчик.\n\n"
                                      "🔄 Напиши /setlang и выбери язык, на который я буду переводить.\n"
                                      "🌐 Просто отправь мне любой текст — и я переведу его!")


@bot.message_handler(commands=['setlang'])
def setlang(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Русский", "English", "Deutsch", "Français", "Español", "日本語", "Қазақша")
    bot.send_message(message.chat.id, "📝 Напиши язык, на который нужно переводить.\n"
                                      "Можешь использовать название или код языка (например, `en`, `русский`)", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def translate_text(message):
    user_id = message.from_user.id
    target_lang = user_langs.get(user_id)

    # Проверка — это установка языка?
    possible_code = normalize_language_code(message.text)
    if possible_code:
        user_langs[user_id] = possible_code
        bot.send_message(message.chat.id, f"✅ Язык перевода установлен на: {LANGUAGES[possible_code].capitalize()}")
        return

    if not target_lang:
        bot.send_message(message.chat.id, "❗ Сначала выбери язык перевода с помощью /setlang")
        return

    # Определяем язык исходного текста
    try:
        source_lang = single_detection(message.text, api="google")
    except Exception:
        source_lang = 'auto'

    # Переводим
    try:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(message.text)
        bot.send_message(message.chat.id, f"💬 Перевод:\n{translated}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка перевода: {e}")


def normalize_language_code(text):
    text = text.lower().strip()

    # Если это код языка
    if text in LANGUAGES:
        return text

    # Если это название на любом языке
    return LANG_CODES.get(text)


@app.route('/')
def home():
    return 'Bot working now!'


def run_flask():
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080)


def run_bot():
    print("Бот запущен...")
    bot.infinity_polling()


def run_server():
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_flask).start()


threading.Thread(target=run_server).start()


