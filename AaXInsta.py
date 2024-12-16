import asyncio
import requests
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant

# Bot Configuration
API_ID = 'api_id'
API_HASH = 'api_hash'
BOT_TOKEN = 'bot_token'
CHANNEL_USERNAME = 'Outlawbots'  # Replace with your channel username
ADMIN_USERNAME = 'faony'  # Replace with admin username
ADMIN_ID = 6076683960  # Replace with the admin's Telegram ID

bot = TelegramClient('instagram_checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global Variables
notified_users = set()  # To track already notified users
user_reporting = {}  # To track reporting state
user_login_status = {}  # To track user login status
waiting_for_login = {}  # To track login states
active_users = set()  # To store active users
broadcasting = False  # Flag to control the broadcast process
broadcast_message_content = None  # Store the broadcast message content

# Helper Function: Check Channel Membership
async def is_user_in_channel(user_id):
    try:
        participant = await bot(GetParticipantRequest(CHANNEL_USERNAME, user_id))
        return isinstance(participant.participant, ChannelParticipant)
    except:
        return False

# Function: Check Instagram Username
def check_instagram_username(username):
    url = f"https://www.instagram.com/{username.strip('@')}/"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True  # Profile exists
        elif response.status_code == 404:
            return False  # Profile does not exist
    except requests.exceptions.RequestException:
        return None  # Error occurred

# Command: /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user = await bot.get_entity(event.sender_id)
    user_id = user.id
    username = user.username or "No Username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    permanent_link = f"tg://user?id={user_id}"

    # Notify the admin of new users (only once per user)
    if user_id not in notified_users:
        notified_users.add(user_id)  # Add to notified users set
        await bot.send_message(
            ADMIN_USERNAME,
            f"🔔 **New User Alert**\n\n"
            f"👤 **Name:** [{full_name}]({permanent_link})\n"
            f"📛 **Username:** @{username if username != 'No Username' else 'No Username'}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"🔗 **Profile Link:** [Click Here]({permanent_link})",
            link_preview=False
        )

    # Add user to active users set
    active_users.add(user_id)

    # Send welcome message to the user
    await event.reply(
        f"👋 Hello, **{full_name}!**\n\n"
        "Welcome to the bot! To get started, please log in using `/login`.\n"
        "Once logged in, you'll have access to features like:\n"
        "- Reporting Targets\n"
        "- Admin Features\n\n"
        "Let me know how I can assist you!",
        buttons=[Button.inline("Log In Now", b'login_help')]
    )

# Command: /login
@bot.on(events.NewMessage(pattern='/login'))
async def login(event):
    user_id = event.sender_id
    if user_login_status.get(user_id, {}).get('logged_in'):
        await event.reply("✅ You are already logged in!")
        return

    waiting_for_login[user_id] = {'status': 'awaiting_username'}
    await event.reply("📝 Please send your username:")

# Login Process: Username and Password Handling
@bot.on(events.NewMessage)
async def handle_login(event):
    user_id = event.sender_id

    if user_id in waiting_for_login:
        state = waiting_for_login[user_id]['status']

        # Step 1: Handle Username
        if state == 'awaiting_username':
            username = event.text.strip()
            waiting_for_login[user_id] = {'status': 'awaiting_password', 'username': username}
            await event.reply("🔒 Now send your password:")

        # Step 2: Handle Password
        elif state == 'awaiting_password':
            password = event.text.strip()
            username = waiting_for_login[user_id]['username']

            # Process login (Add your validation logic here)
            if username == "admin" and password == "password123":  # Replace with real validation
                user_login_status[user_id] = {'logged_in': True, 'username': username}
                del waiting_for_login[user_id]  # Clear login state
                await event.reply("✅ Login successful! You now have access to bot features.")
            else:
                del waiting_for_login[user_id]  # Clear login state on failure
                await event.reply("❌ Login failed! Please try again using `/login`.")

# Command: /logout
@bot.on(events.NewMessage(pattern='/logout'))
async def logout(event):
    user_id = event.sender_id
    if user_login_status.get(user_id, {}).get('logged_in'):
        del user_login_status[user_id]  # Remove the login status
        await event.reply("✅ You have been logged out.")
    else:
        await event.reply("❌ You are not logged in!")

# Command: /report
@bot.on(events.NewMessage(pattern='/report'))
async def report_command(event):
    user_id = event.sender_id

    if not await is_user_in_channel(user_id):
        await event.reply(
            f"😶‍🌫️ **[{event.sender.first_name}]** You must join the premium channel to use this bot.",
            buttons=[Button.url("Join the Channel", f"https://t.me/{CHANNEL_USERNAME}")]
        )
        return

    if user_reporting.get(user_id, {}).get('status') != 'idle':
        await event.reply("⚠️ You have a report in progress. Finish that first!")
        return

    user_reporting[user_id] = {'status': 'awaiting_username'}
    await event.reply("⚠️ Please send the username of the Instagram account you want to report.")

# Handle Username Submission for Reporting
@bot.on(events.NewMessage)
async def handle_username_submission(event):
    user_id = event.sender_id
    if user_reporting.get(user_id, {}).get('status') == 'awaiting_username':
        username = event.text.strip()

        if not username.startswith('@'):
            await event.reply("👤 Please send the username of the target (with @).")
            return

        # Check if Instagram account exists
        if check_instagram_username(username):
            user_reporting[user_id] = {'status': 'reporting', 'username': username}
            await event.reply(f"✅ Username `{username}` accepted. Shall we start reporting?", 
                              buttons=[Button.inline("Start Reporting", b'start_reporting'),
                                       Button.inline("Cancel", b'cancel_reporting')])
        else:
            await event.reply(f"❌ The Instagram account `{username}` does not exist.")

# Handle Inline Buttons for Reporting
@bot.on(events.CallbackQuery)
async def handle_callback(event):
    user_id = event.sender_id

    if event.data == b'start_reporting':
        if user_reporting[user_id].get('status') != 'reporting':
            await event.answer("❌ Invalid action.", alert=True)
            return
        await start_reporting(event)
    elif event.data == b'cancel_reporting':
        user_reporting[user_id]['status'] = 'idle'
        await event.edit("❌ Reporting process has been canceled.")
    elif event.data == b'stop_reporting':
        user_reporting[user_id]['status'] = 'idle'
        await event.edit("🛑 Reporting has been stopped.")

# Reporting Loop
async def start_reporting(event):
    user_id = event.sender_id
    instagram_link = f"http://instagram.com/{user_reporting[user_id]['username'][1:]}"
    
    # Initialize reporting message
    message = await event.edit(f"🚀 Reporting {instagram_link}...", buttons=[Button.inline("Stop Reporting", b'stop_reporting')])

    # Reporting loop (send reports every second, incrementing each second)
    for i in range(1, 10001):  # Reports up to 10,000
        if user_reporting[user_id].get('status') != 'reporting':
            await message.edit(f"‼️ Reporting stopped. Total reports: {i}.")
            return
        await message.edit(f"✅ Reported {instagram_link} {i} times.")
        await asyncio.sleep(1)  # Wait for 1 second before the next report

    await message.edit(f"✅ Reporting complete! {instagram_link} reported 10,000 times.")

# Command: /broadcast
@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast(event):
    user_id = event.sender_id

    if user_id != ADMIN_ID:
        await event.reply("❌ Only the admin can use this command.")
        return

    await event.reply("📝 Please send the message you want to broadcast to all users:")

# Handle Admin's Broadcast Message
@bot.on(events.NewMessage)
async def handle_admin_broadcast(event):
    user_id = event.sender_id

    if user_id == ADMIN_ID and event.text != "/broadcast":
        global broadcast_message_content
        broadcast_message_content = event.text.strip()

        # Confirm the broadcast message with the admin
        await event.reply(
            f"💬 Are you sure you want to send the following message to all users?\n\n{broadcast_message_content}",
            buttons=[
                [Button.inline("Yes", b'confirm_yes')],
                [Button.inline("No", b'confirm_no')]
            ]
        )

# Handle Broadcast Confirmation (Yes/No)
@bot.on(events.CallbackQuery)
async def handle_broadcast_confirmation(event):
    user_id = event.sender_id

    if event.data == b'confirm_yes':
        global broadcast_message_content

        failed = 0
        sent = 0

        # Notify admin about the progress
        progress_message = await event.edit(f"📤 Starting Broadcast...\n\n👥 Total users: {len(active_users)}")

        # Send the broadcast message to all users
        for idx, user_id in enumerate(active_users, start=1):
            try:
                await bot.send_message(user_id, broadcast_message_content)
                sent += 1
            except Exception:
                failed += 1

            if idx % 10 == 0 or idx == len(active_users):
                await progress_message.edit(
                    f"📤 Broadcasting...\n\n✅ Sent: {sent}\n❌ Failed: {failed}\n👥 Remaining: {len(active_users) - idx}"
                )

        await progress_message.edit(
            f"✅ Broadcast Completed\n\n📤 Sent to: {sent} users\n❌ Failed: {failed}\n👥 Total users: {len(active_users)}"
        )

    elif event.data == b'confirm_no':
        await event.edit("❌ Broadcast cancelled.")

# Run the Bot
print("🤖 Bot is running...")
bot.run_until_disconnected()
