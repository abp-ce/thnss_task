import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SAVE_PATH = "users_files/"
DB_NAME = "technesis.sqlite"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
