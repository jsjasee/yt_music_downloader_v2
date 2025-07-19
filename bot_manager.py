import html

from telebot import TeleBot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from api_manager import ApiManager
load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")

# todo: show a message when bot is downloading the song, then delete the message once the song has completed downloading

class BotManager:
    def __init__(self):
        self.bot = TeleBot(token=os.getenv("BOT_TOKEN"))
        self.yt_searcher = ApiManager()
        self.user_state = {}
        self.user_last_message = {}
        self.chosen_song = {}

        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['search'])(self.search_music)
        # self.bot.message_handler(func=lambda message: CHAT_ID in self.user_state and self.user_state[CHAT_ID] == "waiting_for_song")(self.process_search_query)
        # removing the CHAT_ID restriction to message.chat.id
        self.bot.message_handler(
            func=lambda message: message.chat.id in self.user_state and self.user_state[message.chat.id] == "waiting_for_song")(
            self.process_search_query)
        self.bot.callback_query_handler(func=lambda call: True)(self.process_calls)
        # note the callback_query_handler must have a function, and must accept the call, so to make the bot process all calls we just make the function output True everytime

    def run(self):
        self.bot.polling()

    # replacing all CHAT_ID with message.chat.id
    def start(self, message):
        print("Start command received")
        self.bot.send_message(chat_id=message.chat.id, text="🎵 Welcome! Enter /search to start searching for songs.")

    # replacing all CHAT_ID with message.chat.id
    def search_music(self, message):
        self.bot.send_message(chat_id=message.chat.id, text="🔎 Please enter the song name:")
        # change user state to 'searching song'
        self.user_state[message.chat.id] = "waiting_for_song"

    # using .pop() on a list means removes an element at a particular index, eg. .pop(index), using .pop() on dictionary
    # means remove the element but you put the key inside, eg. .pop(key)

    def process_search_query(self, message):
        query = message.text
        self.user_state.pop(message.chat.id) # this removes the key from the self.user_state dictionary, effectively removing the value as well
        results = self.yt_searcher.search(query=query)
        markup = InlineKeyboardMarkup()

        self.chosen_song = {}
        for num in range(len(results)):
            print(results[num])
            self.chosen_song[num] = results[num]
            button = InlineKeyboardButton(text=html.unescape(results[num]['video_title']), callback_data=str(num))
            markup.add(button)

        song_list_msg = self.bot.send_message(message.chat.id, "Choose a song: ", reply_markup=markup)
        self.user_last_message[message.chat.id] = song_list_msg.message_id

    def process_calls(self, call):#instead of message, now we just process the call
        download_in_progress_msg = self.bot.send_message(call.message.chat.id, "Download in progress... ⏳")
        self.bot.delete_message(call.message.chat.id, self.user_last_message[call.message.chat.id])

        # Add the newly sent message to the last message
        self.user_last_message[call.message.chat.id] = download_in_progress_msg.message_id

        song_number = int(call.data)
        video_id = self.chosen_song[song_number]['video_id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        # file_path = self.yt_searcher.download_song(url=youtube_url).replace(".webm", ".mp3")
        # try:
        #     with open(file_path, "rb") as song:
        #         # telegram reads audio files in binary mode, hence rb.
        #         self.bot.send_audio(call.message.chat.id, audio=song, performer=self.chosen_song[song_number]["channel_title"], title=self.chosen_song[song_number]['video_title'], timeout=300)
        #         # open the mp3 file downloaded on computer and then send this file to telegram. make sure to include
        #         # performer and title details so the audio shows up properly on telegram
        # except Exception as e:
        #     # Remove the last message
        #     self.bot.delete_message(call.message.chat.id, self.user_last_message[call.message.chat.id])
        #     self.bot.send_message(call.message.chat.id, f"❌ Error encountered when downloading bot. Please try again: {e}")

        self.bot.send_message(call.message.chat.id,
                              f"Download the song here: https://ezmp3.to/ (or try cnvmp3) 🎉")
        self.bot.send_message(call.message.chat.id, youtube_url, disable_web_page_preview=False)
        # Remove the last message
        self.bot.delete_message(call.message.chat.id, self.user_last_message[call.message.chat.id])

        # if os.path.exists(file_path):
        #     # os is a module, path is a SUB-module inside the os module. .exists() is a function, which checks if the file path exists or not
        #     os.remove(file_path)