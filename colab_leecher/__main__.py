# copyright 2024 © Xron Trix | https://github.com/Xrontrix10

import logging
import os
import asyncio
from pyrogram import filters
from datetime import datetime
from asyncio import sleep
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.handler import cancelTask
from colab_leecher.utility.variables import BOT, MSG, BotTimes, Paths
from colab_leecher.utility.task_manager import task_processor
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from colab_leecher.utility.helper import isLink, setThumbnail, message_deleter, send_settings
from colab_leecher.utility.task_model import Task

# Use an asyncio Queue for thread-safe task management
task_queue = asyncio.Queue()

# You can keep this global if needed for handling message deletion
src_request_msg = None


@colab_bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.delete()
    text = "**Hey There, 👋🏼 It's Colab Leecher**\n\n◲ I am a Powerful File Transloading Bot 🚀\n◲ I can Transfer Files To Telegram or Your Google Drive From Various Sources 🦐\n\n\t \t \t \t <b> This code is modified by 💝 Surya...!!! </b> \n \n <b> Main Owner of this project is - XronTrix10 </b> \n \n <b> Only for testing purpose </b> "
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Repository 🦄",
                    url="https://github.com/XronTrix10/Telegram-Leecher",
                ),
                InlineKeyboardButton("Support 💝", url="https://t.me/Colab_Leecher"),
            ],
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)


@colab_bot.on_message(filters.command("tupload") & filters.private)
async def telegram_upload(client, message):
    global src_request_msg
    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"
    src_request_msg = await message.reply_text(text, quote=True)


@colab_bot.on_message(filters.command("gdupload") & filters.private)
async def drive_upload(client, message):
    global src_request_msg
    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"
    src_request_msg = await message.reply_text(text, quote=True)


@colab_bot.on_message(filters.command("drupload") & filters.private)
async def directory_upload(client, message):
    global src_request_msg
    text = "<b>⚡ Send Me FOLDER PATH 🔗»</b>\n\n🦀 Below is an example\n\n<code>/home/user/Downloads/bot</code>"
    src_request_msg = await message.reply_text(text, quote=True)


@colab_bot.on_message(filters.command("ytupload") & filters.private)
async def yt_upload(client, message):
    global src_request_msg
    text = "<b>⚡ Send YTDL DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}</code>"
    src_request_msg = await message.reply_text(text, quote=True)


@colab_bot.on_message(filters.command("settings") & filters.private)
async def settings(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


@colab_bot.on_message(filters.reply)
async def setPrefix(client, message):
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()


@colab_bot.on_message(filters.create(isLink) & ~filters.photo)
async def handle_url(client, message):
    global BOT
    
    if src_request_msg:
        await src_request_msg.delete()

    temp_source = message.text.splitlines()
    custom_name, zip_pswd, unzip_pswd = "", "", ""

    for _ in range(3):
        if temp_source[-1].startswith("[") and temp_source[-1].endswith("]"):
            custom_name = temp_source.pop()[1:-1]
        elif temp_source[-1].startswith("{") and temp_source[-1].endswith("}"):
            zip_pswd = temp_source.pop()[1:-1]
        elif temp_source[-1].startswith("(") and temp_source[-1].endswith(")"):
            unzip_pswd = temp_source.pop()[1:-1]
        else:
            break

    BOT.Options.custom_name = custom_name
    BOT.Options.zip_pswd = zip_pswd
    BOT.Options.unzip_pswd = unzip_pswd
    BOT.SOURCE = temp_source
    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Regular", callback_data="normal")],
            [
                InlineKeyboardButton("Compress", callback_data="zip"),
                InlineKeyboardButton("Extract", callback_data="unzip"),
            ],
            [InlineKeyboardButton("UnDoubleZip", callback_data="undzip")],
        ]
    )
    
    task_mode = "leech"
    ytdl_mode = False

    task_obj = Task(message, mode=task_mode, ytdl=ytdl_mode, options=BOT.Options, source=BOT.SOURCE)

    await message.reply_text(
        text=f"<b>🐹 Select Type of {task_mode.capitalize()} You Want » </b>\n\nRegular:<i> Normal file upload</i>\nCompress:<i> Zip file upload</i>\nExtract:<i> extract before upload</i>\nUnDoubleZip:<i> Unzip then compress</i>",
        reply_markup=keyboard,
        quote=True,
    )


@colab_bot.on_callback_query()
async def handle_options(client, callback_query):
    if callback_query.data in ["normal", "zip", "unzip", "undzip"]:
        task_mode = "leech"
        ytdl_mode = False
        
        new_task = Task(callback_query.message.reply_to_message, mode=task_mode, ytdl=ytdl_mode, options=BOT.Options, source=BOT.SOURCE)
        new_task.options.mode = callback_query.data
        
        await task_queue.put(new_task)

        await callback_query.message.delete()
        await colab_bot.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )

        status_msg = await colab_bot.send_message(
            chat_id=OWNER,
            text="#STARTING_TASK\n\n**Starting your task in a few Seconds...🦐**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel")],
                ]
            ),
        )
        new_task.set_status_message(status_msg)
        
    elif callback_query.data == "cancel":
        await cancelTask("User Cancelled !")

    # The rest of the `handle_options` function is for settings and remains largely unchanged.


@colab_bot.on_message(filters.photo & filters.private)
async def handle_image(client, message):
    msg = await message.reply_text("<i>Trying To Save Thumbnail...</i>")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("**Thumbnail Successfully Changed ✅**")
        await message.delete()
    else:
        await msg.edit_text(
            "🥲 **Couldn't Set Thumbnail, Please Try Again !**", quote=True
        )
    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("setname") & filters.private)
async def custom_name(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/setname <code>custom_fileame.extension</code>\nTo Set Custom File Name 📛",
            quote=True,
        )
    else:
        BOT.Options.custom_name = message.command[1]
        msg = await message.reply_text(
            "Custom Name Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("zipaswd") & filters.private)
async def zip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/zipaswd <code>password</code>\nTo Set Password for Output Zip File. 🔐",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text(
            "Zip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("unzipaswd") & filters.private)
async def unzip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/unzipaswd <code>password</code>\nTo Set Password to Extract Archives. 🔓",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text(
            "Unzip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    msg = await message.reply_text(
        "Send /start To Check If I am alive 🤨\n\nSend /colabxr and follow prompts to start transloading 🚀\n\nSend /settings to edit bot settings ⚙️\n\nSend /setname To Set Custom File Name 📛\n\nSend /zipaswd To Set Password For Zip File 🔐\n\nSend /unzipaswd To Set Password to Extract Archives 🔓\n\n⚠️ **You can ALWAYS SEND an image To Set it as THUMBNAIL for your files 🌄**",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Instructions 📖",
                        url="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Channel 📣",
                        url="https://t.me/Colab_Leecher",
                    ),
                    InlineKeyboardButton(
                        "Group 💬",
                        url="https://t.me/Colab_Leecher_Discuss",
                    ),
                ],
            ]
        ),
    )
    await sleep(15)
    await message_deleter(message, msg)


async def main():
    # Start the bot
    logging.info("Colab Leecher Started !")
    
    # Start the task processing worker as a background task
    asyncio.create_task(task_processor_worker())

    # This is the corrected structure.
    # The `colab_bot.run()` call should not be here.
    # It will be called once at the top level.
    # `await colab_bot.run()`


async def task_processor_worker():
    while True:
        try:
            task = await task_queue.get()
            await task_processor(task)
            task_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Error in task_processor_worker: {e}")


if __name__ == "__main__":
    # Call `colab_bot.run` and pass the `main()` coroutine to it.
    # This ensures a single event loop is created and managed by Pyrogram.
    colab_bot.run(main())
