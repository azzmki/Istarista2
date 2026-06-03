import telebot
from telebot import types
from config import TOKEN
from database import init_db, save_payment
import os

bot = telebot.TeleBot(TOKEN)  # Token config dan olinadi

# Ma'lumotlar bazasini ishga tushirish
init_db()

# To'lov tugmasi yaratish
def payment_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="1 XTR to'lash", pay=True)
    keyboard.add(button)
    return keyboard

# Boshlash tugmasi yaratish
def start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Rasm sotib olish", callback_data="buy_image")
    keyboard.add(button)
    return keyboard

# /start buyrug'ini qayta ishlash
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Xush kelibsiz! Rasm sotib olish uchun pastdagi tugmani bosing.",
        reply_markup=start_keyboard()
    )

# "Rasm sotib olish" tugmasini qayta ishlash
@bot.callback_query_handler(func=lambda call: call.data == "buy_image")
def handle_buy_image(call):
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

# Muvaffaqiyatli to'lovni qayta ishlash
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

# /paysupport buyrug'ini qayta ishlash
@bot.message_handler(commands=['paysupport'])
def handle_pay_support(message):
    bot.send_message(
        message.chat.id,
        "Rasm sotib olish pulni qaytarishni nazarda tutmaydi. "
        "Savollaringiz bo'lsa, biz bilan bog'lanishingiz mumkin."
    )

# Botni ishga tushirish
bot.polling()