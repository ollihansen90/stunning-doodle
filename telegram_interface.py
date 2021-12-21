import glob
import os
import time
from multiprocessing import Process, Queue

from telegram.ext import CommandHandler, Filters, Updater, MessageHandler

import config
import utils
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot


class TelegramInterface(utils.IEntity):
    def __init__(self, sleep_time=config.ST_TI, bot_token_idx=0):

        self.answer_queue = Queue()
        self.question_queue = Queue()

        bot_token = config.BOT_TOKENS_[bot_token_idx]
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher

        test_handler = CommandHandler(config.CMD_TEST, self.cmd_test)
        dispatcher.add_handler(test_handler)

        start_handler = CommandHandler(config.CMD_START, self.cmd_start)
        dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler(config.CMD_STOP, self.cmd_stop)
        dispatcher.add_handler(stop_handler)

        chat_id_handler = CommandHandler(
            config.CMD_CHAT_ID, self.cmd_get_chat_id)
        dispatcher.add_handler(chat_id_handler)

        message_handler = MessageHandler(
            Filters.text & (~Filters.command), self.received_message)
        dispatcher.add_handler(message_handler)

        self.bot = dispatcher.bot
        self.updater = updater

        self.processes = []

        self.sleep_time = sleep_time

    def run(self):
        p_telegram = Process(target=self.poll_telegram_commands)
        p_telegram.start()
        self.processes.append(p_telegram)

        p_system = Process(target=self.poll_system_commands)
        p_system.start()
        self.processes.append(p_system)

    def received_message(self, update, context):
        print('TI: received message')
        message = utils.Message().from_telegram(update, context)
        print(message.__dict__)
        self.question_queue.put(message)

    def send_message(self, message):
        print('TI: printing message')
        print(message.__dict__)
        self.bot.send_message(message.chat_id, text=message.text)

    # telegram commands
    def cmd_test(self, update, context):
        self.bot.send_message(text="Test", chat_id=get_chat_id(update))

    def cmd_start(self, update, context):
        self.question_queue.put(utils.StartCommand(get_chat_id(update)))
        self.bot.send_message(
            text='Der Chat-bot ist bereit. Schreib doch etwas.',
            chat_id=get_chat_id(update)
        )

    def cmd_stop(self, update, context):
        self.question_queue.put(utils.StopCommand(get_chat_id(update)))

    def cmd_get_chat_id(self, update, context):
        self.bot.send_message(text=str(get_chat_id(update)),
                              chat_id=get_chat_id(update))

    def poll_telegram_commands(self):
        self.updater.start_polling()
        # needs to be used for some reason when in multiprocess
        while True:
            pass

    def poll_system_commands(self):
        while True:
            time.sleep(self.sleep_time)
            if self.answer_queue.empty():
                continue

            message = self.answer_queue.get()
            self.send_message(message)


def get_chat_id(update):
    return update.effective_chat.id

# ----------------------------------------------------------------------------


def _debug():
    from utils import run_safe
    user_interface = TelegramInterface()
    run_safe([user_interface])


if __name__ == "__main__":
    _debug()
