# === AUTO-INSTALL MODULES IF MISSING ===
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
except ImportError:
    install("python-telegram-bot==13.15")
    from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

try:
    from faker import Faker
except ImportError:
    install("faker")
    from faker import Faker

import random
import string
import csv

# === CONFIGURATION ===
BOT_TOKEN = '7736427367:AAHJ-ZvcNVpt-vL65w1-Gjk3eHSb8fto31Y'  # Replace with your bot token
CHANNEL_ID = '-1002044043990'  # Replace with your channel username or '-100...' format
FILENAME = 'fake_data.csv'

# === Initialize Faker ===
fake = Faker()

# === Ensure CSV Exists ===
try:
    with open(FILENAME, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Mobile", "Full Name", "Account No", "IFSC", "Password"])
except FileExistsError:
    pass

# === Generate Fake Data ===
def generate_fake_data():
    return {
        "Mobile": str(random.randint(6000000000, 9999999999)),
        "Full Name": fake.name(),
        "Account No": ''.join(random.choices(string.digits, k=12)),
        "IFSC": fake.bothify(text='SBIN0######').upper(),
        "Password": ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=10))
    }

# === Save to CSV ===
def save_to_csv(data):
    with open(FILENAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([data["Mobile"], data["Full Name"], data["Account No"], data["IFSC"], data["Password"]])

# === Format Message ===
def format_data(data):
    return (
        f"📱 *Mobile*: `{data['Mobile']}`\n"
        f"👤 *Full Name*: `{data['Full Name']}`\n"
        f"🏦 *Account No*: `{data['Account No']}`\n"
        f"🔢 *IFSC*: `{data['IFSC']}`\n"
        f"🔐 *Password*: `{data['Password']}`"
    )

# === Start Command ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 *Fake Data Generator Bot*\n\n"
        "Use /generate to create fake data\n"
        "Use /csv to get the complete CSV file\n"
        "Data will also be posted to the channel",
        parse_mode='Markdown'
    )

# === Send Fake Data to User and Channel ===
def send_fake_data(chat_id, context: CallbackContext):
    data = generate_fake_data()
    save_to_csv(data)

    message = "✅ *Fake Data Generated:*\n\n" + format_data(data)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Regenerate", callback_data='regen')]
    ])

    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

    context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="📋 *New Fake Data:*\n\n" + format_data(data),
        parse_mode='Markdown'
    )

# === /generate Command ===
def generate(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    send_fake_data(chat_id, context)

# === Button Handler ===
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'regen':
        chat_id = query.message.chat_id
        send_fake_data(chat_id, context)

# === /csv Command ===
def send_csv(update: Update, context: CallbackContext):
    try:
        with open(FILENAME, 'rb') as f:
            update.message.reply_document(
                document=InputFile(f, filename="fake_data.csv"),
                caption="📄 Here's the complete CSV file with all generated data"
            )
            f.seek(0)
            context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=InputFile(f, filename="fake_data.csv"),
                caption="📄 Complete Fake Data CSV"
            )
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")

# === Main Entry Point ===
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("generate", generate))
    dp.add_handler(CommandHandler("csv", send_csv))
    dp.add_handler(CallbackQueryHandler(handle_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
