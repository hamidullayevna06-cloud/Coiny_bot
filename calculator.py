import telebot 
import requests
from dotenv import load_dotenv
import os
from telebot import types

load_dotenv(dotenv_path=".env")
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# State management
user_lang = {}    # Stores 'en', 'ru', 'uz'
user_choice = {}  # Stores 'USD', 'EUR', 'RUB'

LANGUAGES = {
    "en": {
        "welcome": "👋 Welcome {name}! Your fast and simple currency converter 💱",
        "lang_set": "✅ Language set to English.",
        "prompt": "How much UZS do you want to convert to {currency}?",
        "result": "✅ {amount:,.0f} UZS = {result:.2f} {currency}",
        "error_num": "⚠️ Please enter a valid number, e.g. 50000",
        "choose_currency": "Please choose a currency first."
    },
    "ru": {
        "welcome": "👋 Добро пожаловать, {name}, в Coiny! Ваш быстрый и простой конвертер валют 💱",
        "lang_set": "✅ Язык установлен на русский.",
        "prompt": "Сколько UZS вы хотите конвертировать в {currency}?",
        "result": "✅ {amount:,.0f} UZS = {result:.2f} {currency}",
        "error_num": "⚠️ Пожалуйста, введите корректное число, например 50000",
        "choose_currency": "Пожалуйста, сначала выберите валюту."
    },
    "uz": {
        "welcome": "👋 Coiny-ga xush kelibsiz, {name}! Tez va oson valyuta ayirboshlash xizmati 💱",
        "lang_set": "✅ Til o'zbek tiliga o'rnatildi.",
        "prompt": "{currency} ga qancha UZS ayirboshlamoqchisiz?",
        "result": "✅ {amount:,.0f} UZS = {result:.2f} {currency}",
        "error_num": "⚠️ Iltimos, to'g'ri son kiriting, masalan 50000",
        "choose_currency": "Iltimos, avval valyutani tanlang."
    }
}

def get_text(chat_id, key, **kwargs):
    lang = user_lang.get(chat_id, "en")
    text = LANGUAGES[lang].get(key, LANGUAGES["en"][key])
    return text.format(**kwargs)

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🇬🇧 English", "🇷🇺 Русский", "🇺🇿 O'zbekcha")
    bot.send_message(message.chat.id, "Select your language / Tilni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    chat_id = message.chat.id
    text = message.text

    # 1. Handle Language Selection
    if text in ["🇬🇧 English", "🇷🇺 Русский", "🇺🇿 O'zbekcha"]:
        mapping = {"🇬🇧 English": "en", "🇷🇺 Русский": "ru", "🇺🇿 O'zbekcha": "uz"}
        user_lang[chat_id] = mapping[text]
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🇺🇸 USD", "🇪🇺 EUR", "🇷🇺 RUB")
        bot.send_message(chat_id, get_text(chat_id, "lang_set"), reply_markup=markup)

    # 2. Handle Currency Selection
    elif text in ["🇺🇸 USD", "🇪🇺 EUR", "🇷🇺 RUB"]:
        if chat_id not in user_lang:
            bot.send_message(chat_id, "Please use /start to set your language first.")
            return
        
        currency = text.split(" ")[1]
        user_choice[chat_id] = currency
        bot.send_message(chat_id, get_text(chat_id, "prompt", currency=currency))

    # 3. Handle Amount (Conversion)
    else:
        currency = user_choice.get(chat_id)
        if not currency:
            bot.send_message(chat_id, get_text(chat_id, "choose_currency"))
            return

        try:
            amount = float(text.replace(",", "").strip())
            response = requests.get(f"https://v6.exchangerate-api.com/v6/{os.getenv('API_KEY')}/latest/UZS")
            data = response.json()
            rate = data["conversion_rates"][currency]
            result = amount * rate
            
            bot.send_message(chat_id, get_text(chat_id, "result", amount=amount, result=result, currency=currency))
            user_choice[chat_id] = None # Reset
        except ValueError:
            bot.send_message(chat_id, get_text(chat_id, "error_num"))
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

bot.polling(non_stop=True)