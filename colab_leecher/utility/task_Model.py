# colab_leecher/utility/task_model.py

from datetime import datetime

class Task:
    def __init__(self, message, mode, ytdl, options, source):
        self.message = message
        self.mode = mode
        self.ytdl = ytdl
        self.options = options
        self.source = source
        self.status_msg = None
        self.start_time = datetime.now()
        self.task_coroutine = None
        
    def set_status_message(self, message):
        self.status_msg = message

    async def update_status(self, text, reply_markup=None):
        if self.status_msg:
            return await self.status_msg.edit_text(text, reply_markup=reply_markup)
