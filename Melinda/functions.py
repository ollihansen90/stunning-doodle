import json
import pickle
import random

import nltk
import numpy as np
import tensorflow
import tflearn
from nltk.stem.lancaster import LancasterStemmer

STEMMER = LancasterStemmer()


def load_model():
    with open('Melinda/intents.json', encoding='utf-8') as file:
        data = json.load(file)

    try:
        with open("Melinda/model/data.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)
        # Runtime Error: Tryblock auskommentieren
    except:
        words = []
        labels = []
        docs_x = []
        docs_y = []

        for intent in data['intents']:
            for pattern in intent['patterns']:
                wrds = nltk.word_tokenize(pattern)  # Satz in Worte aufteilen
                words.extend(wrds)  # zu Wortliste hinzufügen
                docs_x.append(wrds)
                docs_y.append(intent["tag"])

            if intent['tag'] not in labels:
                labels.append(intent['tag'])

        from stopwords import worte
        words = [w for w in words if not w in worte]

        words = [STEMMER.stem(w.lower())
                 for w in words if w != "?"]  # Wortstaemme finden
        words = sorted(list(set(words)))

        labels = sorted(labels)

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(docs_x):
            bag = []

            wrds = [STEMMER.stem(w.lower()) for w in doc]

            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)

            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1

            training.append(bag)
            output.append(output_row)

        training = np.array(training)
        output = np.array(output)

        with open("Melinda/model/data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

    tensorflow.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    #net = tflearn.regression(net)
    net = tflearn.regression(net, loss='categorical_crossentropy')

    model = tflearn.DNN(net)

    # Runtime Error: Tryblock + except auskommentieren
    try:
        model.load("Melinda/model/model.tflearn")
    except:
        raise ValueError
        model.fit(training, output, n_epoch=200,
                  batch_size=8, show_metric=True)
        model.save("Melinda/model/model.tflearn")

    # model.fit(training, output, n_epoch=200, batch_size=8, show_metric=True)
    # model.save("Melinda/model/model.tflearn")

    return model, words, labels, data


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [STEMMER.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)


def predict_answer(message, model, words, labels, data):
    #model, words, labels, data = predict_model()
    message = message.lower()
    results = model.predict([bag_of_words(message, words)])

    results_index = np.argmax(results)
    tag = labels[results_index]

    if results[0, results_index] > 0.9:
        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']
        response = random.choice(responses)
    else:
        response = "Das habe ich leider nicht verstanden!"
    return tag, response


def save_data(save_id, text, name, personal_name):
    #remove name
    if personal_name in text:
        text.replace(personal_name,"*name*")

    save_id = str(save_id)
    try:
        try:
            savefile = open(save_id + ".txt", "a")
            savefile.write(name + ": " + text + "\n \n")
            savefile.close
        except:
            savefile = open(save_id + ".txt", "a")
            savefile.write(name + ": Emoji or Sticker \n \n")
            savefile.close
    except:
        savefile = open(save_id + ".txt", "w+")
        savefile.write(name + ": " + text + "\n \n")
        savefile.close


def save_data_psq20(save_id, text, name, personal_name):
    #remove name
    if personal_name in text:
        text.replace(personal_name,"*name*")
        
    save_id = str(save_id)
    try:
        try:
            savefile = open(save_id + "psq20.txt", "a")
            savefile.write(name + ": " + text + "\n \n")
            savefile.close
        except:
            savefile = open(save_id + "psq20.txt", "a")
            savefile.write(name + ": Emoji or Sticker \n \n")
            savefile.close
    except:
        savefile = open(save_id + "psq20.txt", "w+")
        savefile.write(name + ": " + text + "\n \n")
        savefile.close