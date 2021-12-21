from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import json
from .psq_20 import psq20_response
from .functions import save_data_psq20
from numpy import *
import scipy.linalg
import string



def answer_tree(message, tag, prediction, tree_id, case, name):
    response = []
    new_name = ""

    # tree 0 (start)
    if tree_id == 0:
        if case == 0:
            if case == 0:
                response.append(
                    "Hi, ich bin Melinda! Du kannst mit mir jetzt mit mir schreiben.")
                response.append(
                    "Zu aller erst ist mir aber wichtig zu sagen, dass wir das Gespräch speichern, um es später wissenschaftlich auswerten zu können.")
                response.append(
                    "Aber unser Gespräch wird an der Quelle anonymisiert. Dein Name wird in den Speicherungen nicht mehr auftauchen.")
                response.append(
                    "Nur, wenn das für dich in Ordnung ist, kannst du mit mir schreiben.")
                response.append("Bist du damit einverstanden?")
                case = 0.1

        elif case == 0.1:
            if tag == "good words":
                response.append("Alles klar. Bevor wir starten können, müssen wir noch eine Sache erledigen.")
                response.append(
                    "Damit wir miteinander chatten können, benötige ich noch deinen Key.")
                response.append(
                    "Schreib mir jetzt bitte eine Nachricht, die nur deinen Key enthält. :)")
                case = 0.2
            else:
                response.append("Alles klar, das verstehe ich.")
                response.append("Ich wünsche dir noch einen schönen Tag!")
                case = -1

        elif case == 0.2:
            #check if key is correct
            key = message.text
            if len(key) != 7:
                response.append("Dein Key hat leider die falsche Zeichenanzahl.")
                response.append("Schreib mir bitte jetzt nochmal deinen Key :)")
            else:
                if all(k in string.hexdigits for k in key[0:3]):
                    try:
                        key_hex = int("0x"+key[0:3],0)

                    except:
                        response.append(
                        "Du hast in den ersten 3 Zeichen einen Fehler. Bitte gib deinen Key nochmal ein.")

                    else:
                        if all(k in string.digits for k in key[3:]):
                            try:
                                key_dec = int(key[3:]) - 7
                            except:
                                response.append(
                                    "Du hast in den letzten 4 Zeichen einen Fehler. Bitte gib deinen Key nochmal ein.")
                            else:
                                if key_hex == key_dec:
                                    response.append("Super, dein Key stimmt!")
                                    response.append("Dann kann es jetzt losgehen!")
                                    response.append("Wie heißt du eigentlich? :) Schreib mir bitte nur deinen Namen.")
                                    case = 1
                                else: 
                                    response.append(
                                        "Dein Key stimmt leider nicht. Bitte gib deinen Key nochmal ein.")
                        else:
                            response.append(
                                "Du hast in den letzten 4 Zeichen einen Fehler. Bitte gib deinen Key nochmal ein.")
                else:
                    response.append(
                        "Du hast in den ersten 3 Zeichen einen Fehler. Bitte gib deinen Key nochmal ein.")


        elif case == 1:
            new_name = message.text
            response.append("Also ist " + new_name + " dein Name?")
            case = 2

        elif case == 2:
            if tag == "good words":
                response.append(name + " ist wirklich ein schöner Name!")
                response.append(
                    "Wenn du mit mir schreibst, wirst du manchmal eine Auswahl an Antworten von mir bekommen. Wähle dann am besten auch eine davon aus ^.^")
                response.append("Das wird dann ungefähr so aussehen:")
                response.append("Bist du bereit?")
                case = 3
            else:
                response.append(
                    "Oh, habe ich dich falsch verstanden? Schreib mir deinen Namen jetzt nochmal :)")
                case = 1

        elif case == 3:
            response.append(
                "Hey, das hat doch schon ganz gut geklappt! Dann kann es ja losgehen!")
            response.append("Wie geht es dir gerade " + name + "?")
            case = 0
            tree_id = 1

    # tree 1
    elif tree_id == 1:
        if case == 0:
            if tag == "good words":
                response.append("Das freut mich zu hören!")
                response.append("Hast du aktuell viel zu erledigen?")
                case = 1
            else:
                response.append(
                    "Oh, das tut mir leid. Was beschäftigt dich denn gerade " + name + "?")
                case = 2

        elif case == 1:
            #response.append(prediction)
            if tag == "bad words":
                response.append(
                    "Das ist auch mal ganz angenehm, nicht so viel tun zu müssen.")
            else:
                response.append(
                    "Ich hoffe, dass es noch nicht zu viel ist und dass du genug Kraft hast, um alle deine Aufgaben zu erledigen.")
            response.append("Fühlst du dich voller Energie?")
            case = 0
            tree_id = 2

        elif case == 2:
            if tag == "bad words":
                response.append(
                    "Das ist schön, dass dich nicht so viel beschäftigt.")
                response.append("Fühlst du dich voller Energie?")
                case = 0
                tree_id = 2
            else:
                response.append(
                    "Aktuell ist ja auch viel los. Willst du mir noch mehr darüber erzählen " + name + "?")
                case = 2.1

        elif case == 2.1:
            if tag == "bad words":
                response.append("Das ist okay.")
                response.append("Fühlst du dich voller Energie?")
                case = 0
                tree_id = 2
            else:
                response.append("Okay, dann erzähl mal.")
                case = 2.2

        elif case == 2.2:
            response.append(
                "Ja, das kann ich verstehen. Ich hoffe, dass dich bald weniger belastet!")
            response.append("Fühlst du dich voller Energie?")
            case = 0
            tree_id = 2

    # tree 2
    elif tree_id == 2:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 0)
            response.append(resp)
            response.append("Wie läuft dein Tag bisher " + name + "?")
            case = 1

        elif case == 1:
            if tag == "bad words":
                response.append("Oh, was ist denn heute blöd gewesen? :/")
                case = 2
            else:
                if tag == "good words":
                    response.append(prediction)
                else:
                    response.append("Ah okay, verstehe.")
                response.append(
                    "Würdest du sagen, dass du leichten Herzens bist?")
                case = 0
                tree_id = 3

        elif case == 2:
            response.append("Oh, ja, das kann ich verstehen.")
            response.append("Würdest du sagen, dass du leichten Herzens bist?")
            case = 0
            tree_id = 3

    # tree 3
    elif tree_id == 3:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 1)
            response.append(resp)
            response.append(
                "Ich habe mal ein paar Fragen zu deinem Studium. Hast du eigentlich Kurse in Präsenz?")
            case = 1

        elif case == 1:
            if tag == "bad words":
                response.append("Achso, also nur online Kurse.")
                case = 6
            else:
                response.append(
                    "Dann hast du bestimmt trotzdem Online-Uni gehabt.")
                case = 2
            response.append(
                "Wie war denn das Online Learning für dich letztes Semester " + name + "?")

        elif case == 2:
            response.append(
                "Und wie geht es dir aktuell mit den Hybrid-Unterrichtsformaten?")
            case = 3

        elif case == 3:
            if tag == "bad words":
                response.append("Welche Nachteile siehst du denn?")
            else:
                response.append("Welche Vorteile siehst du denn?")
            case = 4

        elif case == 4:
            response.append(
                "Machst du dir Sorgen bezüglich Covid-19, wenn du vor Ort sein musst " + name + "?")
            case = 5

        elif case == 5:
            if tag == "bad words":
                response.append("Da bin ich ja beruhigt.")
            else:
                response.append(
                    "Ich hoffe, du machst dir nicht zu große Sorgen!")
            response.append(
                "Hast du manchmal das Gefühl, dass dir die Anforderungen zu hoch sind?")
            case = 0
            tree_id = 4

        elif case == 6:
            response.append(prediction)
            response.append(
                "Hast du manchmal das Gefühl, dass dir die Anforderungen zu hoch sind?")
            case = 0
            tree_id = 4

    # tree 4
    elif tree_id == 4:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 2)
            response.append(resp)
            response.append(
                "Während der Pandemie ist das Studentenleben ja stark verändert.")
            response.append(
                "Fühlst du dich in deinem sozialen Leben innerhalb des Studiums eingeschränkt " + name + "?")
            case = 1

        elif case == 1:
            if tag == "bad words":
                response.append("Das freut mich zu hören :)")
                response.append(
                    "Lernst du trotz Covid-19 aktuell in einer Lerngruppe?")
                case = 3
            else:
                response.append("Das tut mir leid :(")
                response.append("Fühlst du dich oft alleine?")
                case = 2

        elif case == 2:
            if tag == "bad words":
                response.append(
                    "Das ist schade :( Die Pandemie ist echt hart...")
            else:
                response.append(
                    "Ah, okay, verstehe. Die Pandemie ist echt hart...")
            response.append(
                "Lernst du trotz Covid-19 aktuell in einer Lerngruppe?")
            case = 3

        elif case == 3:
            response.append("Ah okay.")
            response.append("Bleibt dir noch genügend Zeit für dich selbst?")
            case = 0
            tree_id = 5

    # tree 5
    elif tree_id == 5:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 3)
            response.append(resp)
            response.append("Wie war denn der Kontakt zu deinen Dozierenden?")
            response.append(
                "Hattest du letztes Semester Kontakt zu deinen Dozierenden?")
            case = 1

        elif case == 1:
            if tag == "good words":
                response.append("War der Kontakt ausreichend?")
                case = 2
            else:
                response.append("Oh, hättest du dir mehr Kontakt gewünscht?")
                case = 3

        elif case == 2 or case == 3:
            if case == 2 and tag == "good words":
                response.append("Das freut mich zu hören " + name + "!")
            elif case == 3 and tag == "good words":
                response.append("Okay, danke für die Antwort!")
            else:
                response.append("Okay, das leite ich mal weiter")
            response.append("Fühlst du dich sicher und geborgen?")
            case = 4

        elif case == 4:
            resp = psq20_response(message.text, message.chat_id, 4)
            response.append(resp)
            response.append(
                "Wie war denn die allgemeine Organissation von deinem Studium: Warst du letztes Semester gut informiert, was du tun musstest?")
            case = 0
            tree_id = 6

    # tree 6
    elif tree_id == 6:
        if case == 0:
            if tag == "good words":
                response.append(
                    "Okay. Dann kanntest du auch alle deine Termine, zum Beispiel von Prüfungen?")
                case = 1
            else:
                response.append(
                    "Oh, das ist natürlich ärgerlich :/ Wie war das denn mit deinen Terminen:")
                response.append("Fühlst du dich unter Termindruck?")
                case = 0
                tree_id = 7

        elif case == 1:
            if tag == "bad words":
                response.append("Mhh, okay.")
            else:
                response.append("Das ist gut!")
            response.append("Fühlst du dich unter Termindruck?")
            case == 0
            tree_id = 7

    # tree 7
    elif tree_id == 7:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 5)
            response.append(resp)
            response.append(
                "In diesem Semester war ja auch die Lehre ganz anders.")
            response.append(
                "Glaubst du denn, dass du auf den Alltag als Arzt gut vorbereitet wirst " + name + "?")
            case = 1

        elif case == 1:
            response.append(prediction)
            response.append("Eine Frage hätte ich noch:")
            response.append(
                "Hälst du Schauspielpatienten für eine gute Alternative zu echten Patienten?")
            case = 0
            tree_id = 8

    # tree 8
    elif tree_id == 8:
        if case == 0:
            if tag == "good words":
                response.append("Freut mich, dass das für dich gut klappt :)")
            else:
                response.append("Verstehe.")
            response.append(
                "Hast du das Gefühl, dass du weißt, was dich inhaltlich dieses Semester erwartet?")
            case = 1

        elif case == 1:
            response.append(prediction)
            response.append(
                "Und weißt du, was dich dieses Semester ablauftechnisch erwartet?")
            case = 2

        elif case == 2:
            response.append("Alles klar.")
            response.append("Hast du momentan viel zu tun?")
            case = 3

        elif case == 3:
            resp = psq20_response(message.text, message.chat_id, 6)
            response.append(resp)
            if message.text == "immer" or message.text == "häufig":
                response.append("Würdest du gerne mehr Unterstützung haben?")
                case = 4
            else:
                response.append(
                    "Würdest du allgemein sagen, dass dich dein Studium stresst " + name + "?")
                case = 0
                tree_id = 9

        elif case == 4:
            response.append("Okay.")
            response.append(
                "Würdest du allgemein sagen, dass dich dein Studium stresst " + name + "?")
            case = 0
            tree_id = 9

    # tree 9
    elif tree_id == 9:
        if case == 0:
            if tag == "good words":
                response.append(
                    "Ohje, das klingt ja nicht so gut :( Was stresst dich denn?")
                case = 1
            # elif tag == "bad words":
            else:
                response.append(
                    "Das ist schön zu hören. Und abgesehen vom Studium...")
                response.append("Fühlst du dich gehetzt?")
                tree_id = 10

        elif case == 1:
            response.append("Das klingt sehr stressig...")
            response.append("Fühlst du dich gehetzt?")
            case = 0
            tree_id = 10

    # tree 10
    elif tree_id == 10:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 7)
            response.append(resp)
            response.append("Und allgemein: ")
            response.append("Machst du Dinge, die du wirklich magst?")
            case = 1

        elif case == 1:
            resp = psq20_response(message.text, message.chat_id, 8)
            response.append(resp)
            if message.text == "immer" or message.text == "häufig":
                response.append(
                    "Was machst du denn in deiner Freizeit (zum Beispiel ein Hobby)?")
                case = 2
            else:
                response.append("Aber hast du ein Hobby?")
                case = 4

        elif case == 2:
            response.append("Wie hilft dir dein Hobby beim entspannen " + name + "?")
            case = 3

        elif case == 3:
            if tag == "bad words":
                response.append(
                    "Das ist ja schade, dass du damit nicht entspannen kannst.")
            else:
                response.append(
                    "Das klingt nach einem schönen Hobby. Ich hänge viel zu viel in Chatrooms ab.")
            response.append("Und allgemein in deiner Freizeit: ")
            response.append("Hast du Spaß?")
            case = 0
            tree_id = 11

        elif case == 4:
            if tag == "bad words":
                response.append(
                    "Mhh, das ist ja schade. Wie ist das sonst in deiner Freizeit: ")
                response.append("Hast du Spaß?")
                case = 0
                tree_id = 11
            else:
                response.append("Was ist denn dein Hobby?")
                case = 5

        elif case == 5:
            response.append(
                "Das klingt nach einem schönen Hobby. Ich verbringe meine Freizeit am liebsten mit chatten!")
            response.append("Und allgemein in deiner Freizeit: ")
            response.append("Hast du Spaß?")
            case = 0
            tree_id = 11

    # Tree 11
    elif tree_id == 11:
        if case == 0:
            resp = psq20_response(message.text, message.chat_id, 9)
            response.append(resp)
            response.append("Puhh, danke, jetzt hast du auch erstmal alle meine Fragen beantwortet!")
            ques = random.choice(["Hast du sonst noch etwas, das du mir erzählen möchtest " + name + "?", "Gibt es noch mehr zu erzählen?", 
                "Hast du sonst noch was auf dem Herzen " + name + "?", "Willst du noch was loswerden?"])
            response.append(ques)
            case = 1
        elif case == 1:
            if tag == "bad words":
                response.append("Alles klar :)")
                response.append("Vielen Dank für deine Teilnahme und dass du es so lange mit mir ausgehalten hast!")
                response.append("Machs gut " + name + "!")
                case = 3 
            else:
                response.append("Dann erzähl doch mal :)")
                case = 2
        elif case == 2:
            ans = random.choice(["Aha. Interessant!", "Spannend.", "Ach so.", "Hmm...", "Sowas habe ich ja noch nie gehört!", "Sachen gibts."])
            ques = random.choice(["Hast du sonst noch etwas, das du mir erzählen möchtest?", "Gibt es noch mehr zu erzählen?," 
                "Hast du sonst noch was auf dem Herzen?", "Willst du noch was loswerden " + name + "?"])
            response.append(ans)
            response.append(ques)
            case = 1

    # End Trees
    else:
        response.append(prediction)

    return response, tree_id, case, new_name