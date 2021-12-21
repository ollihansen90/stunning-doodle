import sys
import config
import utils
import multiprocessing as mp
import time
sys.path.append(config.PATH_TO_FLASK_BACKEND)


class WebInterface(utils.IEntity):
    def __init__(self):
        import app

        self.receive_from_app = app.send_qu
        self.send_to_app = app.receive_qu
        self.answer_queue = mp.Queue()
        self.question_queue = mp.Queue()

        self.processes = [
            mp.Process(target=app.app.run),
            mp.Process(target=self._run)
        ]

    def run(self):
        for proc in self.processes:
            proc.start()

    def _run(self):
        print('Starting reader')
        while True:
            if not self.receive_from_app.empty():
                data = self.receive_from_app.get()
                self.handle_received(data)

            elif not self.answer_queue.empty():
                message = self.answer_queue.get()
                out = {
                    'userId': message.chat_id,
                    'message': message.text
                }
                if message.buttons is not None:
                    out['buttons'] = message.buttons

                self.send_to_app.put(out)

            else:
                time.sleep(.1)

    def handle_received(self, data):
        # first check all commands
        for command in [self.cmd_start, self.cmd_stop, self.cmd_test, self.cmd_get_chat_id]:
            if command(data):
                return

        # input is a message
        message = utils.Message(
            chat_id=get_chat_id(data),
            text=data['message']
        )
        self.question_queue.put(message)

    def cmd_test(self, data):
        if data['message'] == '/' + config.CMD_TEST:
            data['message'] = 'test'
            self.send_to_app.put(data)
            return True
        return False

    def cmd_get_chat_id(self, data):
        if data['message'] == '/' + config.CMD_CHAT_ID:
            data['message'] = get_chat_id(data)
            self.send_to_app.put(data)
            return True
        return False

    def cmd_start(self, data):
        if data['message'] == '/' + config.CMD_START:
            message = utils.StartCommand(get_chat_id(data))
            self.question_queue.put(message)

            data['message'] = 'Der Chat-bot ist bereit. Schreib doch etwas.'
            self.send_to_app.put(data)
            return True
        return False

    def cmd_stop(self, data):
        if data['message'] == '/' + config.CMD_STOP:
            message = utils.StopCommand(get_chat_id(data))
            self.question_queue.put(message)
            return True
        return False


def get_chat_id(data):
    return data['userId']


def _debug():
    web_interface = WebInterface(mp.Queue(), mp.Queue())
    web_interface.run()


if __name__ == '__main__':
    _debug()
