import telebot
from flask import Flask, request
from config import TOKEN
from database import init_db, save_payment
import os
import threading

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Ma'lumotlar bazasini ishga tushirish
init_db()

# To'lov tugmasi yaratish
def payment_keyboard():
    from telebot import types
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="1 XTR to'lash", pay=True)
    keyboard.add(button)
    return keyboard

# Boshlash tugmasi yaratish
def start_keyboard():
    from telebot import types
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Rasm sotib olish", callback_data="buy_image")
    keyboard.add(button)
    return keyboard

# /start buyrug'i
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Xush kelibsiz! Rasm sotib olish uchun pastdagi tugmani bosing.",
        reply_markup=start_keyboard()
    )

# "Rasm sotib olish" tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "buy_image")
def handle_buy_image(call):
    from telebot import types
    prices = [types.LabeledPrice(label="XTR", amount=1)]
    bot.send_invoice(
        call.message.chat.id,
        title="Rasm sotib olish",
        description="1 yulduzga rasm sotib olish!",
        invoice_payload="image_purchase_payload",
        provider_token="",
        currency="XTR",
        prices=prices,
        reply_markup=payment_keyboard()
    )

# To'lovni tekshirish
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Muvaffaqiyatli to'lov
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    user_id = message.from_user.id
    payment_id = message.successful_payment.provider_payment_charge_id
    amount = message.successful_payment.total_amount
    currency = message.successful_payment.currency

    bot.send_message(message.chat.id, "✅ To'lov qabul qilindi, rasmni kuting. Tez orada keladi!")
    
    save_payment(user_id, payment_id, amount, currency)

    photo_path = 'img/telegram_stars.jpg'
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="🥳 Sotib olganingiz uchun rahmat! 🤗")
    else:
        bot.send_message(message.chat.id, "Kechirasiz, rasm topilmadi.")

# Health check endpoint (Render uchun)
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

# Webhook endpoint
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

# Webhook'ni o'rnatish
WEBHOOK_URL = os.getenv('RENDER_EXTERNAL_URL', '')
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")
    print(f"Webhook o'rnatildi: {WEBHOOK_URL}/webhook/{TOKEN}")
else:
    print("RENDER_EXTERNAL_URL topilmadi, polling rejimida ishga tushmoqda...")
    def run_polling():
        bot.infinity_polling()
    thread = threading.Thread(target=run_polling)
    thread.start()

# Flask serverni ishga tushirish (Render uchun)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)