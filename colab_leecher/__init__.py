# copyright 2024 © Xron Trix | https://github.com/Xrontrix10

import os
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, DUMP_ID, OWNER, LOG_URL

if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as log:
        log.truncate(0)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler()
    ]
)

logging.getLogger('pyrogram').setLevel(logging.ERROR)

colab_bot = Client(
    'Colab_Leecher',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root='colab_leecher')
)

logging.info("Starting Colab Leecher... Wait!")
