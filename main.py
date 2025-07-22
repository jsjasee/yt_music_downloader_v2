from bot_manager import BotManager
from flask import Flask, request
# from threading import Thread
import requests, os
from telebot import types
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

bot_manager = BotManager()
bot = bot_manager.bot
app = Flask(__name__)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# Optional root route for confirmation
@app.route("/")
def home():
    return "Bot is running with polling."

@app.route("/test-telegram")
def test_telegram():
    token = os.getenv("BOT_TOKEN")  # Replace with your bot token
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return f"Telegram API is reachable: {response.json()}", 200
    except requests.exceptions.RequestException as e:
        return f"Error reaching Telegram API: {e}", 500

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = request.get_data().decode("utf-8")
        print(update)
        try:
            bot.process_new_updates([types.Update.de_json(update)])
        except Exception as e:
            print(f'Could not process update, error: {e}')
        return '', 200
    return 'Invalid content type', 403

# Start the bot with polling
if __name__ == "__main__":
    # print("Starting bot with polling...")
    # Thread(target=bot.run).start()
    # Start Flask app to satisfy Render's port requirement
    app.run(host="0.0.0.0", port=5001)

# if hosting on railway, do add a 'Procfile', then type in 'worker: python main.py'