import argparse

import chat_bot as cb
import communicator
import config
import telegram_interface
import utils
from Melinda import TelegramPSQ20Interviewer


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot_idx', type=int, default=0)

    return parser.parse_args()


def run(options):
    # create entities
    # chatbot manager needs a class object to initiate objects
    chat_bot = cb.ChatBotManager(cb.Melinda)
    user_interface = telegram_interface.TelegramInterface(
        bot_token_idx=options.bot_idx
    )

    interviewer = TelegramPSQ20Interviewer(
        config.BOT_TOKENS_[options.bot_idx]
    )

    com_unit = communicator.Communicator(
        user_interface, chat_bot, interviewer=interviewer
    )

    # start processes
    utils.run_safe([
        chat_bot,
        com_unit,
        user_interface
    ])


if __name__ == "__main__":
    OPTIONS = get_options()
    run(OPTIONS)
