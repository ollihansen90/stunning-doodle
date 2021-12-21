import argparse

import chat_bot as cb
import communicator
import config
import web_interface
import utils
from Melinda import WebPSQ20Interviewer


def run():
    # create entities
    # chatbot manager needs a class object to initiate objects
    user_interface = web_interface.WebInterface()

    interviewer = WebPSQ20Interviewer(
        user_interface.send_to_app
    )
    chat_bot = cb.ChatBotManagerWeb(cb.Melinda, interviewer)

    com_unit = communicator.Communicator(
        user_interface, chat_bot
    )

    # start processes
    utils.run_safe([
        chat_bot,
        com_unit,
        user_interface
    ])


if __name__ == "__main__":
    run()
