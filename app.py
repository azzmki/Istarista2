import telebot
from flask import Flask, request
import os
import sqlite3

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Ma'lumotlar bazasi
def init_db():
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                payment_id TEXT,
                amount INTEGER,
                currency TEXT
            )
        ''')
        conn.commit()

def save_payment(user_id, payment_id, amount, currency):
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, payment_id, amount, currency)
            VALUES (?, ?, ?, ?)
        ''', (user_id, payment_id, amount, currency))
        conn.commit()

init_db()

# Bot handlerlar
from telebot import types

def payment_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="1 XTR to'lash", pay=True)
    keyboard.add(button)
    return keyboard

def start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Rasm sotib olish", callback_data="buy_image")
    keyboard.add(button)
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Xush kelibsiz! Rasm sotib olish uchun pastdagi tugmani bosing.", reply_markup=start_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "buy_image")
def handle_buy_image(call):
    prices = [types.LabeledPrice(label="XTR", amount=1)]
    bot.send_invoice(call.message.chat.id, title="Rasm sotib olish", description="1 yulduzga rasm sotib olish!", invoice_payload="image_purchase_payload", provider_token="", currency="XTR", prices=prices, reply_markup=payment_keyboard())

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    user_id = message.from_user.id
    payment_id = message.successful_payment.provider_payment_charge_id
    amount = message.successful_payment.total_amount
    currency = message.successful_payment.currency
    bot.send_message(message.chat.id, "✅ To'lov qabul qilindi, rasmni kuting!")
    save_payment(user_id, payment_id, amount, currency)
    photo_path = 'img/telegram_stars.jpg'
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="🥳 Rahmat! 🤗")
    else:
        bot.send_message(message.chat.id, "Kechirasiz, rasm topilmadi.")

# Webhook endpoint
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
if WEBHOOK_URL:
    @app.route(f'/webhook/{TOKEN}', methods=['POST'])
    def webhook():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        return 'Bad Request', 400
    
    @app.route('/health', methods=['GET'])
    def health():
        return 'OK', 200
    
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")
    print(f"Webhook o'rnatildi: {WEBHOOK_URL}/webhook/{TOKEN}")
else:
    print("RENDER_EXTERNAL_URL topilmadi")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)