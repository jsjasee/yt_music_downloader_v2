from bot_manager import BotManager
from flask import Flask
from threading import Thread
import requests, os
import imageio_ffmpeg

# ffmpeg_binary = imageio_ffmpeg.get_ffmpeg_exe()
# os.environ["PATH"] = os.path.dirname(ffmpeg_binary) + os.pathsep + os.environ["PATH"]

bot = BotManager()
app = Flask(__name__)

# Optional root route for confirmation
@app.route("/")
def home():
    return "Bot is running with polling."

@app.route("/test-telegram")
def test_telegram():
    token = os.getenv("TOKEN")  # Replace with your bot token
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return f"Telegram API is reachable: {response.json()}", 200
    except requests.exceptions.RequestException as e:
        return f"Error reaching Telegram API: {e}", 500

# Start the bot with polling
if __name__ == "__main__":
    print("Starting bot with polling...")
    Thread(target=bot.run).start()
    # Start Flask app to satisfy Render's port requirement
    app.run(host="0.0.0.0", port=5001)

# if hosting on railway, do add a 'Procfile', then type in 'worker: python main.py'