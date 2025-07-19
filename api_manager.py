import base64
import os
from youtube_api import YouTubeDataAPI
from dotenv import load_dotenv
load_dotenv()
from yt_dlp import YoutubeDL

# todo 1: get the relevant api keys for youtube api and bot credentials...
# todo 2: see if gunicorn works once hosted on render
# todo 3: analyse the code and see why threading is necessary
API_KEY = os.getenv("YT_API_KEY")
# USERNAME = os.getenv("COMPUTER_USER_NAME")

# Decode base64 string and save as cookies.txt
cookies_b64 = os.getenv("COOKIES_B64")
cookies_path = "/tmp/cookies.txt"

if cookies_b64:
    with open(cookies_path, "wb") as file:
        file.write(base64.b64decode(cookies_b64))
else:
    print("Missing COOKIES_B64 env variable")

class ApiManager:
    def __init__(self):
        self.yt_api = YouTubeDataAPI(API_KEY)
        self.yt_downloader_options = {
        'format': 'bestaudio/best',
        # 'cookiefile': cookies_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': "/tmp/%(title)s.%(ext)s", # f'/Users/{USERNAME}/Downloads/%(title)s.%(ext)s', #directory to save the mp3 file, the % will allow the computer to modify the file name later. # tmp is a temporary file storage that can be used on Render
        'quiet': True,
        'external_downloader': 'aria2c', # 🔹 Use Aria2 as an external downloader
        }
        self.youtube_downloader = YoutubeDL(self.yt_downloader_options)

        # The % symbol is part of string formatting in Python.
        # In this case, '%(title)s.%(ext)s' is a template where yt-dlp automatically replaces placeholders (%(title)s, %(ext)s) with actual values.
        # %(title)s	is replaced with The YouTube video title ("Imagine Dragons - Believer")
        # %(ext)s is replaced with The file extension ("mp3") -> ext means extension

    def search(self,query):
        results = self.yt_api.search(q=query, max_results=10)
        print(results)
        return results

    def download_song(self, url):
        mp3_info = self.youtube_downloader.extract_info(url=url, download=True)
        print("Running the function: download_song")
        print(self.youtube_downloader.prepare_filename(mp3_info))
        return self.youtube_downloader.prepare_filename(mp3_info)