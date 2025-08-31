# copyright 2024 © Xron Trix | https://github.com/Xrontrix10

import pytz
import shutil
import logging
from time import time
from datetime import datetime
from asyncio import sleep
from os import makedirs, path as ospath, system
from colab_leecher import OWNER, colab_bot, DUMP_ID
from colab_leecher.downlader.manager import calDownSize, get_d_name, downloadManager
from colab_leecher.utility.helper import (
    getSize,
    applyCustomName,
    keyboard,
    sysINFO,
    is_google_drive,
    is_telegram,
    is_ytdl_link,
    is_mega,
    is_terabox,
    is_torrent,
)
from colab_leecher.utility.handler import (
    Leech,
    Unzip_Handler,
    Zip_Handler,
    SendLogs,
    cancelTask,
)
from colab_leecher.utility.variables import (
    BOT,
    MSG,
    BotTimes,
    Messages,
    Paths,
    Aria2c,
    Transfer,
    TaskError,
)

async def task_processor(task):
    """
    This function processes a single task from the queue.
    It encapsulates all the logic for a single download/upload cycle.
    """
    
    is_dualzip, is_unzip, is_zip, is_dir = (
        task.options.mode == "undzip",
        task.options.mode == "unzip",
        task.options.mode == "zip",
        task.mode == "dir-leech",
    )
    
    # Reset Texts & Transfer data using the task object
    Messages.download_name = ""
    Messages.task_msg = f"<b>🦞 TASK MODE » </b>"
    Messages.dump_task = (
        Messages.task_msg
        + f"<i>{task.options.mode.capitalize()} {task.mode.capitalize()} as {BOT.Setting.stream_upload}</i>\n\n<b>🖇️ SOURCES » </b>"
    )
    Transfer.sent_file = []
    Transfer.sent_file_names = []
    Transfer.down_bytes = [0, 0]
    Transfer.up_bytes = [0, 0]
    Messages.download_name = ""
    Messages.task_msg = ""
    Messages.status_head = f"<b>📥 DOWNLOADING » </b>\n"
    
    src_text = []

    if is_dir:
        if not ospath.exists(task.source[0]):
            TaskError.state = True
            TaskError.text = "Task Failed. Because: Provided Directory Path Not Exists"
            logging.error(TaskError.text)
            return
        if not ospath.exists(Paths.temp_dirleech_path):
            makedirs(Paths.temp_dirleech_path)
        Messages.dump_task += f"\n\n📂 <code>{task.source[0]}</code>"
        Transfer.total_down_size = getSize(task.source[0])
        Messages.download_name = ospath.basename(task.source[0])
    else:
        for link in task.source:
            if is_telegram(link):
                ida = "💬"
            elif is_google_drive(link):
                ida = "♻️"
            elif is_torrent(link):
                ida = "🧲"
                Messages.caution_msg = "\n\n⚠️<i><b> Torrents Are Strictly Prohibited in Google Colab</b>, Try to avoid Magnets !</i>"
            elif is_ytdl_link(link):
                ida = "🏮"
            elif is_terabox(link):
                ida = "🍑"
            elif is_mega(link):
                ida = "💾"
            else:
                ida = "🔗"
            code_link = f"\n\n{ida} <code>{link}</code>"
            if len(Messages.dump_task + code_link) >= 4096:
                src_text.append(Messages.dump_task)
                Messages.dump_task = code_link
            else:
                Messages.dump_task += code_link

    # Get the current date and time in the specified time zone
    cdt = datetime.now(pytz.timezone("Asia/Kolkata"))
    dt = cdt.strftime(" %d-%m-%Y")
    Messages.dump_task += f"\n\n<b>📆 Task Date » </b><i>{dt}</i>"

    src_text.append(Messages.dump_task)

    if ospath.exists(Paths.WORK_PATH):
        shutil.rmtree(Paths.WORK_PATH)
        makedirs(Paths.down_path)
    else:
        makedirs(Paths.WORK_PATH)
        makedirs(Paths.down_path)
    Messages.link_p = str(DUMP_ID)[4:]

    try:
        system(f"aria2c -d {Paths.WORK_PATH} -o Hero.jpg {Aria2c.pic_dwn_url}")
    except Exception:
        Paths.HERO_IMAGE = Paths.DEFAULT_HERO

    MSG.sent_msg = await colab_bot.send_message(chat_id=DUMP_ID, text=src_text[0])

    if len(src_text) > 1:
        for lin in range(1, len(src_text)):
            MSG.sent_msg = await MSG.sent_msg.reply_text(text=src_text[lin], quote=True)

    Messages.src_link = f"https://t.me/c/{Messages.link_p}/{MSG.sent_msg.id}"
    Messages.task_msg += f"__[{task.options.mode.capitalize()} {task.mode.capitalize()} as {BOT.Setting.stream_upload}]({Messages.src_link})__\n\n"

    await task.status_msg.delete()
    img = Paths.THMB_PATH if ospath.exists(Paths.THMB_PATH) else Paths.HERO_IMAGE
    task.status_msg = await colab_bot.send_photo(  # type: ignore
        chat_id=OWNER,
        photo=img,
        caption=Messages.task_msg
        + Messages.status_head
        + f"\n📝 __Starting DOWNLOAD...__"
        + sysINFO(),
        reply_markup=keyboard(),
    )

    await calDownSize(task.source)

    if not is_dir:
        await get_d_name(task.source[0])
    else:
        Messages.download_name = ospath.basename(task.source[0])

    if is_zip:
        Paths.down_path = ospath.join(Paths.down_path, Messages.download_name)
        if not ospath.exists(Paths.down_path):
            makedirs(Paths.down_path)

    task.start_time = datetime.now()

    if task.mode != "mirror":
        await Do_Leech(task, task.source, is_dir, task.ytdl, is_zip, is_unzip, is_dualzip)
    else:
        await Do_Mirror(task, task.source, task.ytdl, is_zip, is_unzip, is_dualzip)


async def Do_Leech(task, source, is_dir, is_ytdl, is_zip, is_unzip, is_dualzip):
    if is_dir:
        for s in source:
            if not ospath.exists(s):
                logging.error("Provided directory does not exist !")
                await cancelTask("Provided directory does not exist !")
                return
            Paths.down_path = s
            if is_zip:
                await Zip_Handler(task, Paths.down_path, True, False)
                await Leech(task, Paths.temp_zpath, True)
            elif is_unzip:
                await Unzip_Handler(task, Paths.down_path, False)
                await Leech(task, Paths.temp_unzip_path, True)
            elif is_dualzip:
                await Unzip_Handler(task, Paths.down_path, False)
                await Zip_Handler(task, Paths.temp_unzip_path, True, True)
                await Leech(task, Paths.temp_zpath, True)
            else:
                if ospath.isdir(s):
                    await Leech(task, Paths.down_path, False)
                else:
                    Transfer.total_down_size = ospath.getsize(s)
                    makedirs(Paths.temp_dirleech_path)
                    shutil.copy(s, Paths.temp_dirleech_path)
                    Messages.download_name = ospath.basename(s)
                    await Leech(task, Paths.temp_dirleech_path, True)
    else:
        await downloadManager(source, is_ytdl)

        Transfer.total_down_size = getSize(Paths.down_path)

        # Renaming Files With Custom Name
        applyCustomName()

        # Preparing To Upload
        if is_zip:
            await Zip_Handler(task, Paths.down_path, True, True)
            await Leech(task, Paths.temp_zpath, True)
        elif is_unzip:
            await Unzip_Handler(task, Paths.down_path, True)
            await Leech(task, Paths.temp_unzip_path, True)
        elif is_dualzip:
            print("Got into un doubled zip")
            await Unzip_Handler(task, Paths.down_path, True)
            await Zip_Handler(task, Paths.temp_unzip_path, True, True)
            await Leech(task, Paths.temp_zpath, True)
        else:
            await Leech(task, Paths.down_path, True)

    await SendLogs(task, True)


async def Do_Mirror(task, source, is_ytdl, is_zip, is_unzip, is_dualzip):
    if not ospath.exists(Paths.MOUNTED_DRIVE):
        await cancelTask("Google Drive is NOT MOUNTED ! Stop the Bot and Run the Google Drive Cell to Mount, then Try again !")
        return

    if not ospath.exists(Paths.mirror_dir):
        makedirs(Paths.mirror_dir)

    await downloadManager(source, is_ytdl)

    Transfer.total_down_size = getSize(Paths.down_path)

    applyCustomName()

    cdt = datetime.now()
    cdt_ = cdt.strftime("Uploaded » %Y-%m-%d %H:%M:%S")
    mirror_dir_ = ospath.join(Paths.mirror_dir, cdt_)

    if is_zip:
        await Zip_Handler(task, Paths.down_path, True, True)
        shutil.copytree(Paths.temp_zpath, mirror_dir_)
    elif is_unzip:
        await Unzip_Handler(task, Paths.down_path, True)
        shutil.copytree(Paths.temp_unzip_path, mirror_dir_)
    elif is_dualzip:
        await Unzip_Handler(task, Paths.down_path, True)
        await Zip_Handler(task, Paths.temp_unzip_path, True, True)
        shutil.copytree(Paths.temp_zpath, mirror_dir_)
    else:
        shutil.copytree(Paths.down_path, mirror_dir_)

    await SendLogs(task, False)
