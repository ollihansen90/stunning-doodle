import time


def run_safe(entities):
    """When running without this processes may not stop with ctrl+c 

    Parameters
    ----------
    entities : list of IEntity
        object that runs one or several processes
    """
    for entity in entities:
        entity.run()
    while True:
        try:
            time.sleep(30)
        except:
            print('Closing all processes')
            for entity in entities:
                for proc in entity.processes:
                    proc.terminate()

            return -1


class IEntity(object):
    def __init__(self):
        self.processes = list()

    def run(self):
        raise NotImplementedError


class Message():
    def __init__(self, chat_id=None, text=None, buttons=None):
        self.chat_id = chat_id
        self.text = text
        self.buttons = None

    def update(self, text=None, buttons=None, chat_id=None):
        if self.text is None:
            self.text = text
        else:
            self.text += '\n ' + text

        if self.chat_id is None:
            self.chat_id = chat_id
        else:
            if not self.chat_id == chat_id:
                print(f'{self.chat_id} is not {chat_id}')

        if buttons is not None:
            assert self.buttons is None, 'Buttons already set.'
            self.buttons = buttons

    def from_telegram(self, update, context):
        self.chat_id = update.effective_chat.id
        self.text = update.message.text

        return self


class StartCommand():
    def __init__(self, chat_id):
        self.chat_id = chat_id


class StopCommand():
    def __init__(self, chat_id):
        self.chat_id = chat_id


class PSQ20Question():
    def __init__(self, text, chat_id):
        self.chat_id = chat_id
        self.text = text
