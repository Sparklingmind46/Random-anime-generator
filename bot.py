from pyrogram import Client, filters
import requests
import random
import os
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup  

TOKEN = os.environ.get("TOKEN", "")
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

app = Client("anime-gen", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

regex_photo = ["waifu", "neko"]

@app.on_callback_query()
async def handle_query(client, query):
    if query.data == "again":
        try:
            pht = random.choice(regex_photo)
            url = f"https://api.waifu.pics/sfw/{pht}"
            response = requests.get(url).json()
            up = response.get('url')

            if up:
                but = [[InlineKeyboardButton("Generate again ✨", callback_data='again')],
                       [InlineKeyboardButton("Source Code 🌺", url='https://github.com/prime-hritu/Anime-Generator-Bot')]]
                markup = InlineKeyboardMarkup(but)
                await query.message.reply_photo(up, caption="**@AIanimeGenBot**", reply_markup=markup)
            else:
                await query.message.reply("Request failed. Please try again.")
        except Exception as e:
            await query.message.reply(f"An error occurred: {str(e)}")

@app.on_message(filters.private)
async def get_waifu(client, message):
    try:
        pht = random.choice(regex_photo)
        url = f"https://api.waifu.pics/sfw/{pht}"
        response = requests.get(url).json()
        up = response.get('url')

        if up:
            button = [[InlineKeyboardButton("Generate again ✨", callback_data='again')]]
            markup = InlineKeyboardMarkup(button)
            message.reply_photo(up, caption="**@AIanimeGenBot**", reply_markup=markup)
        else:
            message.reply("Request failed. Please try again.")
    except Exception as e:
        message.reply(f"An error occurred: {str(e)}")

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "Welcome to the Anime Image Generator Bot!\n\n"
        "🎨 This bot fetches random anime wallpapers for you. Use the 'Generate again' button to get a new wallpaper.\n\n"
        "**👨‍💻 Developer: [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝ ](https://t.me/ur_amit_01)**"
    )
    await message.reply_text(welcome_text)

app.run()
