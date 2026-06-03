import telebot
from telebot import types
import os
import sqlite3
from datetime import datetime

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ========== MA'LUMOTLAR BAZASI ==========
def init_db():
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        # Foydalanuvchilar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                stars INTEGER DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # To'lovlar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                stars INTEGER,
                status TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def get_user(user_id):
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            return (user_id, 0, 0, datetime.now())
        return user

def update_balance(user_id, amount):
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

def add_stars(user_id, stars):
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET stars = stars + ? WHERE user_id = ?', (stars, user_id))
        conn.commit()

init_db()

# ========== ASOSIY KLAVIATURA ==========
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "🏠 Bosh sahifa",
        "⭐ Stars",
        "🎁 Gift",
        "💳 Hisob to'ldirish",
        "📊 Kabinet",
        "🆘 Yordam"
    ]
    keyboard.add(*buttons)
    return keyboard

# ========== INLINE TUGMALAR ==========
def profile_inline():
    """Kabinet uchun inline tugmalar"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("⭐ 1 Star - 190 so'm", callback_data="buy_1"),
        types.InlineKeyboardButton("⭐ 5 Stars - 900 so'm", callback_data="buy_5"),
        types.InlineKeyboardButton("⭐ 10 Stars - 1700 so'm", callback_data="buy_10"),
        types.InlineKeyboardButton("⭐ 25 Stars - 4000 so'm", callback_data="buy_25"),
        types.InlineKeyboardButton("🎁 Gift yuborish", callback_data="gift"),
        types.InlineKeyboardButton("📊 Tranzaksiyalar", callback_data="transactions"),
        types.InlineKeyboardButton("🆘 Yordam", callback_data="help"),
        types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="home")
    ]
    keyboard.add(*buttons)
    return keyboard

def buy_keyboard():
    """Xarid qilish tugmalari"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("⭐ 1 Star - 190 so'm", callback_data="buy_1"),
        types.InlineKeyboardButton("⭐ 5 Stars - 900 so'm", callback_data="buy_5"),
        types.InlineKeyboardButton("⭐ 10 Stars - 1700 so'm", callback_data="buy_10"),
        types.InlineKeyboardButton("⭐ 25 Stars - 4000 so'm", callback_data="buy_25"),
        types.InlineKeyboardButton("◀️ Orqaga", callback_data="back_to_home")
    ]
    keyboard.add(*buttons)
    return keyboard

# ========== BOT HANDLERLAR ==========
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    # Profil kartasi
    profile_text = (
        f"👋 Assalomu alaykum, @{message.from_user.username or 'user'}\n\n"
        f"🆔 User ID: {user_id}\n"
        f"💰 Balans: {user[1]} so'm\n"
        f"⭐ Stars: {user[2]} ta\n"
        f"📅 Qo'shilgan: {user[3][:10]}\n\n"
        f"💡 Quyidagi tugmalardan foydalanishingiz mumkin:"
    )
    
    bot.send_message(
        message.chat.id,
        profile_text,
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if message.text == "🏠 Bosh sahifa" or message.text == "◀️ Orqaga":
        profile_text = (
            f"👋 Assalomu alaykum, @{message.from_user.username or 'user'}\n\n"
            f"🆔 User ID: {user_id}\n"
            f"💰 Balans: {user[1]} so'm\n"
            f"⭐ Stars: {user[2]} ta\n"
            f"📅 Qo'shilgan: {user[3][:10]}"
        )
        bot.send_message(message.chat.id, profile_text, reply_markup=main_keyboard())
    
    elif message.text == "📊 Kabinet":
        profile_text = (
            f"📊 **SIZNING KABINETINGIZ** 📊\n\n"
            f"🆔 ID: {user_id}\n"
            f"💰 Balans: {user[1]} so'm\n"
            f"⭐ Stars: {user[2]} ta\n"
            f"📅 Ro'yxatdan: {user[3][:10]}\n\n"
            f"⭐ Star narxlari:\n"
            f"• 1 Star - 190 so'm\n"
            f"• 5 Star - 900 so'm\n"
            f"• 10 Star - 1700 so'm\n"
            f"• 25 Star - 4000 so'm"
        )
        bot.send_message(message.chat.id, profile_text, parse_mode="Markdown", reply_markup=profile_inline())
    
    elif message.text == "⭐ Stars":
        bot.send_message(
            message.chat.id,
            "⭐ **STAR SOTIB OLISH** ⭐\n\nQuyidagi paketlardan birini tanlang:",
            parse_mode="Markdown",
            reply_markup=buy_keyboard()
        )
    
    elif message.text == "💳 Hisob to'ldirish":
        bot.send_message(
            message.chat.id,
            "💳 **HISOB TO'LDIRISH** 💳\n\n"
            "Hisobingizni to'ldirish uchun quyidagi tugmalardan foydalaning:",
            parse_mode="Markdown",
            reply_markup=buy_keyboard()
        )
    
    elif message.text == "🎁 Gift":
        bot.send_message(
            message.chat.id,
            "🎁 **GIFT YUBORISH** 🎁\n\n"
            "Do'stingizga Star sovg'a qilish uchun:\n"
            "/gift @username 5\n\n"
            "Misol: /gift @dostim 10"
        )
    
    elif message.text == "🆘 Yordam":
        help_text = (
            "🆘 **YORDAM** 🆘\n\n"
            "📌 **Buyruqlar:**\n"
            "/start - Botni qayta ishga tushirish\n"
            "/balance - Balansni ko'rish\n"
            "/gift - Gift yuborish\n"
            "/support - Qo'llab-quvvatlash\n\n"
            "📞 **Bog'lanish:** @admin_username\n"
            "📧 Email: support@example.com"
        )
        bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# ========== INLINE CALLBACKLAR ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if call.data.startswith("buy_"):
        stars = int(call.data.split("_")[1])
        prices = {
            1: 190,
            5: 900,
            10: 1700,
            25: 4000
        }
        price = prices.get(stars, 190)
        
        # Telegram Stars orqali to'lov
        amounts = [types.LabeledPrice(label=f"{stars} Star", amount=stars)]
        
        try:
            bot.send_invoice(
                call.message.chat.id,
                title=f"⭐ {stars} Star sotib olish",
                description=f"{stars} star - {price} so'm",
                invoice_payload=f"stars_{stars}",
                provider_token="",
                currency="XTR",
                prices=amounts,
                reply_markup=None
            )
        except Exception as e:
            bot.answer_callback_query(call.id, f"Xatolik: {e}")
    
    elif call.data == "gift":
        bot.answer_callback_query(call.id, "Gift yuborish: /gift @username 5")
        bot.send_message(call.message.chat.id, "🎁 Gift yuborish uchun: /gift @username 5")
    
    elif call.data == "transactions":
        with sqlite3.connect('payments.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY date DESC LIMIT 10', (user_id,))
            transactions = cursor.fetchall()
        
        if transactions:
            text = "📊 **So'nggi tranzaksiyalar:**\n\n"
            for t in transactions:
                text += f"• {t[5][:10]} - {t[2]} so'm - {t[3]} Star - {t[4]}\n"
        else:
            text = "📊 Hech qanday tranzaksiya topilmadi."
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=profile_inline())
    
    elif call.data == "help":
        help_text = (
            "🆘 **YORDAM** 🆘\n\n"
            "1. Star sotib oling\n"
            "2. Gift yuboring\n"
            "3. Hisobingizni to'ldiring\n\n"
            "❓ Savollar bo'lsa: @admin_username"
        )
        bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=profile_inline())
    
    elif call.data == "back_to_home":
        profile_text = (
            f"🏠 **BOSH SAHIFA**\n\n"
            f"💰 Balans: {user[1]} so'm\n"
            f"⭐ Stars: {user[2]} ta"
        )
        bot.edit_message_text(profile_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_keyboard())
    
    elif call.data == "home":
        profile_text = (
            f"👋 Assalomu alaykum, @{call.from_user.username or 'user'}\n\n"
            f"🆔 User ID: {user_id}\n"
            f"💰 Balans: {user[1]} so'm\n"
            f"⭐ Stars: {user[2]} ta"
        )
        bot.edit_message_text(profile_text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard())
    
    bot.answer_callback_query(call.id)

# ========== GIFT BUYRUG'I ==========
@bot.message_handler(commands=['gift'])
def handle_gift(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ To'g'ri format: /gift @username 5")
            return
        
        username = parts[1].replace('@', '')
        stars = int(parts[2])
        
        sender_id = message.from_user.id
        sender = get_user(sender_id)
        
        if sender[2] < stars:
            bot.send_message(message.chat.id, f"❌ Sizda {stars} star yetarli emas! Sizda {sender[2]} star bor.")
            return
        
        # Star yuborish (bu yerda real foydalanuvchini topish kerak)
        bot.send_message(message.chat.id, f"✅ {stars} star @{username} ga yuborildi!")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik: {e}")

@bot.message_handler(commands=['balance'])
def handle_balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 Sizning balansingiz: {user[1]} so'm\n⭐ Sizda {user[2]} star bor.")

# ========== TO'LOV HANDLERLARI ==========
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    user_id = message.from_user.id
    stars = int(message.successful_payment.invoice_payload.split("_")[1])
    
    add_stars(user_id, stars)
    
    # To'lovni saqlash
    with sqlite3.connect('payments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, amount, stars, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message.successful_payment.total_amount, stars, "completed"))
        conn.commit()
    
    bot.send_message(
        message.chat.id,
        f"✅ To'lov muvaffaqiyatli!\n\n⭐ Siz {stars} star sotib oldingiz!\n💰 Jami: {message.successful_payment.total_amount} XTR"
    )
    
    # Yangi balansni ko'rsatish
    user = get_user(user_id)
    bot.send_message(
        message.chat.id,
        f"📊 Yangi balans:\n💰 {user[1]} so'm\n⭐ {user[2]} star"
    )

print("🚀 Bot ishga tushdi...")
bot.infinity_polling()