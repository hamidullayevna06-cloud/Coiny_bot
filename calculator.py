import telebot 
import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
import os
from telebot import types



bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# Start and Dreeting

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🇺🇸 USD")
    btn2 = types.KeyboardButton("🇪🇺 EUR")
    btn3 = types.KeyboardButton("🇷🇺 RUB")
    markup.row(btn1, btn2, btn3)

    # send photo with caption
    file = open("greeting_photo.jpg", "rb")
    bot.send_photo(message.chat.id, file)



    bot.send_message(message.chat.id,
        f"👋 Welcome {name} to Coiny!\n"
        "Your fast and simple currency converter 💱"
    )
    print("message sent")
    # send buttons
    bot.reply_to(message, "Choose a currency to convert from UZS:", reply_markup=markup)


    
 

    


    

user_choice = {} # this stores which currency the user picked

@bot.message_handler(func=lambda message: True)
def handle_currency(message):
    chat_id = message.chat.id

    if message.text in ["🇺🇸 USD", "🇪🇺 EUR", "🇷🇺 RUB"]:
        # Extract currency code from button text (e.g., "🇺🇸 USD" -> "USD")
        currency = message.text.split(" ")[1]
        user_choice[chat_id] = currency
        bot.send_message(chat_id, f"How much UZS do you want to convert to {currency}?")

    else:
        currency = user_choice.get(chat_id)

        if currency:
            try:
                # Fixed the typo here (.strip())
                amount = float(message.text.replace(",", "").strip())
                
                # Fixed the duplicate assignment
                response = requests.get(f"https://v6.exchangerate-api.com/v6/{os.getenv('API_KEY')}/latest/UZS")
                data = response.json()

                rate = data["conversion_rates"][currency]
                result = amount * rate

                bot.send_message(chat_id, f"✅ {amount:,.0f} UZS = {result:.2f} {currency}")
                user_choice[chat_id] = None # Reset after result
                start(message) # Restart flow

            except ValueError:
                bot.send_message(chat_id, "⚠️ Please enter a valid number, e.g. 50000")
            except Exception as e:
                print("ERROR:", e)
                bot.send_message(chat_id, f"❌ Something went wrong: {e}")
        else:
            bot.send_message(chat_id, "Please choose a currency first using the buttons below.")







bot.polling(non_stop=True)