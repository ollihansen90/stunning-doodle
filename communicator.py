import os
import time

import config
import utils
from multiprocessing import Process


class Communicator(utils.IEntity):
    def __init__(self, user_interface, chat_bot, interviewer=None, sleep_time=config.ST_COM):
        self.ui = user_interface
        self.chat_bot = chat_bot
        self.sleep_time = sleep_time
        self.interviewer = interviewer

        self.processes = []

    def run(self):
        self.processes.append(Process(target=self._run))
        self.processes[0].start()

    def _run(self):
        while True:
            if not self.ui.question_queue.empty():
                user_message = self.ui.question_queue.get()
                if isinstance(user_message, utils.Message):
                    self._question_bot(user_message)
                elif isinstance(user_message, utils.StartCommand):
                    self._question_bot(user_message)
                elif isinstance(user_message, utils.StopCommand):
                    self._question_bot(user_message)
                else:
                    raise ValueError('unknown input')

            elif not self.chat_bot.answer_queue.empty():
                bot_message = self.chat_bot.answer_queue.get()
                if isinstance(bot_message, utils.Message):
                    self._send_message(bot_message)
                elif isinstance(bot_message, utils.PSQ20Question):
                    self.interviewer.question(
                        bot_message.text, bot_message.chat_id
                    )
            else:
                time.sleep(self.sleep_time)

    def _send_message(self, message):
        self.ui.answer_queue.put(message)

    def _question_bot(self, message):
        self.chat_bot.question_queue.put(message)
