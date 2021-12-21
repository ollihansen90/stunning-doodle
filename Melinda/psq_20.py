import json
import requests
from .functions import save_data_psq20
import time
import random
from .psq20_answers import psq20_answers


class TelegramPSQ20Interviewer():
    def __init__(self, token):
        self.token = token
        self.questions = psq20_questions

    def question(self, text, chat_id):
        telegram_send_psq20_question(text, self.token, chat_id)


class WebPSQ20Interviewer():
    def __init__(self, web_interface_qu):
        self.qu = web_interface_qu

    def question(self, text, chat_id):
        return web_send_psq20_question(text, self.qu, chat_id)


def web_send_psq20_question(text, web_interface_qu, chat_id):
    time.sleep(3.5)
    if text == "Bist du bereit?":
        text += "\nWähle eine der folgenden Antworten aus:"
        reply_markup = ["Jaaa :)", "Na klar!", "Auf jeden Fall!", "Absolut!"]
        return {'chat_id': chat_id, 'text': text, 'buttons': reply_markup}
    else:
        text += "\nWähle eine der folgenden Antworten aus:"
        reply_markup = ["fast nie", "manchmal", "häufig", "immer"]
        data = {'userId': chat_id, 'message': text, 'buttons': reply_markup}
        save_data_psq20(chat_id, text, "Melinda", "")
        return {'chat_id': chat_id, 'text': text, 'buttons': reply_markup}


def telegram_send_psq20_question(text, token, chat_id):
    time.sleep(3.5)
    if text == "Bist du bereit?":
        text += "\nWähle eine der folgenden Antworten aus:"
        reply_markup = {"keyboard": [["Jaaa :)", "Na klar!"], [
            "Auf jeden Fall!", "Absolut!"]], "one_time_keyboard": True}
        datas = {'chat_id': chat_id, 'text': text,
                 'reply_markup': json.dumps(reply_markup)}
        url = "https://api.telegram.org/bot" + token + "/sendMessage"
        r = requests.get(url, data=datas)

    else:
        text += "\nWähle eine der folgenden Antworten aus:"
        reply_markup = {"keyboard": [["fast nie", "manchmal"], [
            "häufig", "immer"]], "one_time_keyboard": True}
        datas = {'chat_id': chat_id, 'text': text,
                 'reply_markup': json.dumps(reply_markup)}
        url = "https://api.telegram.org/bot" + token + "/sendMessage"
        r = requests.get(url, data=datas)
        save_data_psq20(chat_id, text, "Melinda", "")


def psq20_response(message, chat_id, answer_id):
    save_data_psq20(chat_id, message, "Person", "")
    try:
        index1 = ["fast nie", "manchmal", "häufig", "immer"].index(message)
        index2 = random.choice([0,1,2])
        resp = psq20_answers[answer_id][index1][index2]
    except:
        resp = "Alles klar :)"
    return resp

def psq20_response_old(message, chat_id, answer_id):
    save_data_psq20(chat_id, message, "Person", "")
    a1 = random.choice(["Das tut mir leid", "Das ist sehr schade",
                        "Mhh, das ist nicht so schön", "Ohje, das klingt nicht so gut"])
    a2 = random.choice(["Ich hoffe es wird bald besser",
                        "Gib dem ganzen noch ein bisschen Zeit", "Mh verstehe"])
    a3 = random.choice(["Du bist auf einem guten Weg",
                        "Das klingt ja schonmal nicht schlecht!", "Das ist ja schonmal ganz gut"])
    a4 = random.choice(["Das freut mich zu hören",
                        "Das ist sehr schön", "Das ist super", "Klingt gut!"])

    if answer_id == 0:
        if message == "fast nie":
            resp = a4
        elif message == "manchmal":
            resp = a3
        elif message == "häufig":
            resp = a2
        else:
            resp = a1
    else:
        if message == "immer":
            resp = a4
        elif message == "häufig":
            resp = a3
        elif message == "manchmal":
            resp = a2
        else:
            resp = a1
    return resp



psq20_questions = ["Hast du momentan viel zu tun?",
                   "Fühlst du dich voller Energie?",
                   "Hast du manchmal das Gefühl, dass dir die Anforderungen zu hoch sind?",
                   "Machst du Dinge, die du wirklich magst?",
                   "Fühlst du dich gehetzt?",
                   "Fühlst du dich sicher und geborgen?",
                   "Hast du Spaß?",
                   "Würdest du sagen, dass du leichten Herzens bist?",
                   "Hast du genügend Zeit für dich selbst?",
                   "Fühlst du dich unter Termindruck?"]