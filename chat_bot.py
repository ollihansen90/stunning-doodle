import random
import time
from multiprocessing import Process, Queue

import config
import utils
from Melinda import (answer_tree, load_model, predict_answer, psq20_questions,
                     save_data)


class IBotProcess(utils.IEntity):
    def __init__(self, sleep_time=config.ST_CB):
        self.question_queue = Queue()
        self.answer_queue = Queue()
        self.sleep_time = sleep_time
        self.processes = []

    def run(self):
        self.processes.append(Process(target=self._run))
        self.processes[0].start()

    def _run(self):
        raise NotImplementedError


class ChatBotManager(IBotProcess):
    def __init__(self, cls_object, sleep_time=config.ST_CB):
        super(ChatBotManager, self).__init__()
        self.bot_dict = dict()
        self.cls_obj = cls_object

    def _start(self, chat_id):
        print(self)
        new_obj = self.cls_obj(chat_id)
        self.bot_dict[chat_id] = new_obj
        print(f'Created new bot chat_id {chat_id}')
        print(self.bot_dict.keys())

    def _stop(self, chat_id):
        self.bot_dict.pop(chat_id)
        print(f'Removed chat_id {chat_id}')
        print(self.bot_dict.keys())

    def _run(self):
        while True:
            if self.question_queue.empty():
                time.sleep(self.sleep_time)
            else:
                message = self.question_queue.get()
                self._relay(message)

    def _relay(self, message):
        # is it a signal to add/delete an id?
        if isinstance(message, utils.StartCommand):
            self._start(message.chat_id)
            return
        elif isinstance(message, utils.StopCommand):
            self._stop(message.chat_id)
            return

        assert isinstance(message, utils.Message)

        # assume chat_id is in bot_dict otherwise answer
        if not message.chat_id in self.bot_dict.keys():
            answers_ = self._answer_key_no_found(message.chat_id)
            self.put_answers(answers_)
            return

        answers_ = self.bot_dict[message.chat_id]._answer(message)
        self.put_answers(answers_)

    def put_answers(self, answers_):
        for answer in answers_:
            assert isinstance(answer, (utils.Message, utils.PSQ20Question))
            self.answer_queue.put(answer)

    def _answer_key_no_found(self, chat_id):
        answer = utils.Message(
            chat_id=chat_id,
            text="Chat-Bot mit /start initialisieren."
        )

        return [answer]


class ChatBotManagerWeb(ChatBotManager):
    def __init__(self, cls_object, interviewer, sleep_time=config.ST_CB):

        self.interviewer = interviewer
        super(ChatBotManagerWeb, self).__init__(cls_object,
                                                sleep_time=config.ST_CB)

    def put_answers(self, answers_):
        print('putting answer')
        big_message = utils.Message()
        for answer in answers_:
            if isinstance(answer, utils.Message):
                big_message.update(answer.text, chat_id=answer.chat_id)
            elif isinstance(answer, utils.PSQ20Question):
                aswr_dict = self.interviewer.question(
                    answer.text, answer.chat_id,
                )
                big_message.update(
                    aswr_dict['text'], buttons=aswr_dict['buttons']
                )

        print(big_message.__dict__)
        self.answer_queue.put(big_message)


class Melinda():
    def __init__(self, chat_id):
        self.chat_id = chat_id

        self.tree_id = 0
        self.case = 0
        self.name = ""

        model, words, labels, data = load_model()
        self.model = model
        self.words = words
        self.labels = labels
        self.data = data

    def _answer(self, message):
        output = []
        save_data(message.chat_id, message.text, "Person", self.name)

        tag, response = predict_answer(
            message.text,
            self.model, self.words, self.labels, self.data
        )
        response, new_tree_id, new_case, new_name = answer_tree(
            message, tag, response, self.tree_id, self.case, self.name
        )

        self.tree_id = new_tree_id
        self.case = new_case
        if new_name != "":
            self.name = new_name

        for resp in response:
            if resp not in psq20_questions and resp != "Bist du bereit?":
                answer = utils.Message(
                    chat_id=self.chat_id,
                    text=resp
                )
                output.append(answer)
            else:
                answer = utils.PSQ20Question(
                    text=resp,
                    chat_id=self.chat_id
                )
                output.append(answer)

            save_data(message.chat_id, resp, "Melinda", self.name)

        return output


class ManagedBot():
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def _answer(self, message):
        answer = utils.Message(
            chat_id=self.chat_id,
            text=f"Ich antworte nur im Raum {self.chat_id}"
        )

        return [answer]


class StupidChatbot(IBotProcess):
    def __init__(self, sleep_time=config.ST_CB):
        super(StupidChatbot, self).__init__()

    def _run(self):
        while True:
            if self.question_queue.empty():
                time.sleep(self.sleep_time)
            else:
                message = self.question_queue.get()
                self._answer(message)

    def _answer(self, message):
        print('CB: received:')
        print(message.__dict__)
        answer = utils.Message(
            chat_id=message.chat_id,
            text=random.choice([
                'Was?',
                'Wie bitte?',
                'Kapier ich nicht!',
                'Ich nix verstehen!'
            ])
        )
        print('CB: send:')
        print(answer.__dict__)
        self.answer_queue.put(answer)

