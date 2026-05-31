import telebot 
import requests
from dotenv import load_dotenv
import os
from telebot import types

load_dotenv()

bot = telebot.TeleBot("BOT_TOKEN")

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


    if message.text == "🇺🇸 USD":
        user_choice[chat_id] = "USD"
        bot.send_message(chat_id, "How much UZS do ypu wnat to convert to USD?")

    elif message.text == "🇪🇺 EUR":
        user_choice[chat_id] = "EUR"
        bot.send_message(chat_id, "How much UZS do you want to convert to EUR?")

    elif message.text == "🇷🇺 RUB":
        user_choice[chat_id] = "RUB"
        bot.send_message(chat_id, "How much UZS do you want to convert to RUB?")

    else:
        currency = user_choice.get(chat_id)
        print(f"chat_id: {chat_id}")        # ← see the chat id
        print(f"currency: {currency}")       # ← see what's stored
        print(f"message: {message.text}")    # ← see what user sent

        if currency:
            try:
                amount = float(message.text.replace(",", ""))
                #fetch real time retes 
                response = response = requests.get(f"https://v6.exchangerate-api.com/v6/{os.getenv('API_KEY')}/latest/UZS")
                data = response.json()
                print(data)

                rate = data["conversion_rates"][currency]
                result = amount * rate

                bot.send_message(chat_id, f"✅ {amount} UZS = {result:.2f} {currency}")
                user_choice[chat_id]= None #reset after result
                start(message) # calls existing function again


            except:
                bot.send_message(chat_id, "⚠️ Please send a valid number!")







bot.polling(non_stop=True)