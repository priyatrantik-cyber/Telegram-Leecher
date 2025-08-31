# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import logging, json, os
from uvloop import install
from pyrogram.client import Client

# Try loading credentials.json if it exists
cred_file = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
cred_file = os.path.abspath(cred_file)

credentials = {}

if os.path.exists(cred_file):
    with open(cred_file, "r") as file:
        credentials = json.load(file)

# API credentials (first from JSON, else from env vars)
API_ID = credentials.get("API_ID") or os.getenv("API_ID")
API_HASH = credentials.get("API_HASH") or os.getenv("API_HASH")
BOT_TOKEN = credentials.get("BOT_TOKEN") or os.getenv("BOT_TOKEN")
OWNER = credentials.get("USER_ID") or os.getenv("USER_ID")
DUMP_ID = credentials.get("DUMP_ID") or os.getenv("DUMP_ID")

# Basic logging
logging.basicConfig(level=logging.INFO)

# Use uvloop
install()

# Initialize Pyrogram bot
colab_bot = Client(
    "my_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
