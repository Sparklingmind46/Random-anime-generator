from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import random
import os

# Get the bot token from environment variables
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found. Please set it as an environment variable.")
    
def start(update, context):
    """Send a welcome message and explain the bot's functionality."""
    welcome_text = (
        "Welcome to the Anime Image Bot!\n\n"
        "🎨 This bot fetches random anime wallpapers for you. Use the 'Refresh' button to get a new wallpaper."
    )
    update.message.reply_text(welcome_text)

def get_anime(update, context):
    """Send a random anime image."""
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔁 Refresh", callback_data="anime_edit")]])
    ran = random.randint(100000, 999999999)
    anime = f"https://ashlynn.serv00.net/husbando.php?r={ran}"
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=anime, reply_markup=markup)

def refresh_anime(update, context):
    """Edit the current message to show a new anime image."""
    query = update.callback_query
    ran = random.randint(100000, 999999999)
    anime = f"https://ashlynn.serv00.net/husbando.php?r={ran}"
    media = InputMediaPhoto(media=anime)
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔁 Refresh", callback_data="anime_edit")]])
    query.edit_message_media(media, reply_markup=markup)

# Main function to run the bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("anime", get_anime))
    dispatcher.add_handler(CallbackQueryHandler(refresh_anime, pattern="anime_edit"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
