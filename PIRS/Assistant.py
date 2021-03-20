import pyaudio
from datetime import datetime
import webbrowser as wb
from fuzzywuzzy import fuzz
from os import system
from random import choice
from playsound import playsound
from PyQt5 import QtCore
from recognizer import Recognizer

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
TIMEOUT_LENGTH = 3
SAMPLE_WIDTH = 2
SHORT_NORMALIZE = 1.0 / 32768.0
Energy_speech = 10
key_word = 'пирс'

# Phrases
phrases_for_executing = ["Doing.mp3", "Will_be_done.mp3", "How_say_sir.mp3"]
phrases_for_web_search = ["Finding_information 1.mp3", "Finding_information 2.mp3", "Request_accepted.mp3"]

""" ---> Voice Assistant <--- """


class Assistant(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.rc = Recognizer()
        # default commands of PIRS
        self.tasks = {
            # internet and social networks
            ("открой ютуб", "запусти ютуб"): self.youtube,
            ("открой вк", "запусти вк"): self.vk,
            # system commands and windows apps
            ("открой диспетчер задач", "запусти диспетчер задач"): self.taskmgr,
            ("открой панель управления", "запусти панель управления"): self.control,
            ("открой проводник", "запусти проводник", "открой мой компьютер", "запусти мой компьютер"): self.explorer,
            ("открой параметры", "запусти параметры"): self.params,
            ("выключи компьютер", "выключи пк"): self.turn_off,
            ("перезагрузи компьютер", "перезагрузи пк"): self.refresh,
            ("открой калькулятор", "запусти калькулятор"): self.calc,
            ("пока", "заверши работу"): self.bye
        }

    def voice_activation(self):
        while True:
            if self.rc.start():
                self.cmd(self.rc.speech_to_text())

    # commands execution
    def cmd(self, task):
        self.feedDict(self.tasks)

        max_similar = 0  # the coefficient of similarity
        cmd = ''  # command
        search_tags = ("как", "кто такой", "кто такая", "что такое", "найди", "ищи", "найти")

        # inaccurate search
        for ls in self.tasks:
            for i in ls:
                rate_similar = fuzz.ratio(task, i)
                if rate_similar > 75 and rate_similar > max_similar:
                    max_similar = rate_similar
                    cmd = ls
        try:
            try:
                self.open_site(self.tasks[cmd])
            except:
                self.tasks[cmd]()
        except KeyError:
            for tag in search_tags:
                if tag in task:
                    return self.web_search(task.replace(tag, ""))
            playsound("audio/Repeat_please.mp3")
            new_task = self.rc.speech_to_text()
            if new_task != "":
                self.cmd(new_task)

    # Choosing random phrase for executing command
    @staticmethod
    def random_phrase(pr_phrase=None):
        phrase_exe = choice(phrases_for_executing)
        phrase = choice([phrase_exe, pr_phrase])
        audio_file = f"audio/{phrase}"
        playsound(audio_file, block=False)

    @staticmethod
    def random_phrase_web():
        phrase = choice(phrases_for_web_search)
        audio_file = f"audio/{phrase}"
        playsound(audio_file, block=False)

    def open_site(self, url):
        wb.open(url)
        self.random_phrase("Opening.mp3")

    # getting commands from file "command.txt"
    def downloadCommand(self):
        with open("commands.txt") as file:
            for line in file:
                uc = line.replace("\n", "")
                uc = uc.split(";")
                url = uc[0]
                command = uc[1]
                self.tasks[tuple([command])] = url

    @staticmethod
    def countFunc():
        with open("commands.txt") as file:
            n = sum(1 for line in file)
        return n

    def feedDict(self, dict):
        count = 10 + self.countFunc()
        if count != len(dict):
            self.downloadCommand()

    # Functions for user
    def youtube(self):
        self.random_phrase("Youtube.mp3")
        return wb.open("https://www.youtube.com/")

    def vk(self):
        self.random_phrase("Vk.mp3")
        return wb.open("https://vk.com/")

    def web_search(self, task):
        self.random_phrase_web()
        return wb.open(f"https://www.google.com/search?q={task}&sourceid=chrome&ie=UTF-8".replace(" ", "+"))

    def taskmgr(self):
        self.random_phrase("Opening.mp3")
        return system("taskmgr")

    def control(self):
        self.random_phrase("Control_panel.mp3")
        return system("control")

    def explorer(self):
        self.random_phrase("Opening.mp3")
        return system("explorer")

    def calc(self):
        self.random_phrase("Launching_Calculator.mp3")
        return system("start calc")

    def params(self):
        self.random_phrase("Opening.mp3")
        return system("dpiscaling")

    def turn_off(self):
        playsound("audio/Confirm_action.mp3")
        if self.speech_to_text() == "подтверждаю":
            self.random_phrase()
            return system("shutdown /s /t ")
        else:
            return playsound("audio/How_say_sir.mp3")

    def refresh(self):
        playsound("audio/Confirm_action.mp3")
        if self.speech_to_text() == "подтверждаю":
            self.random_phrase()
            return system("shutdown /r /t ")
        else:
            return playsound("audio/How_say_sir.mp3")

    @staticmethod
    def greeting():
        current_time = datetime.now()
        if (current_time.hour >= 6) and (current_time.hour < 12):
            playsound(r"audio\Good_morning.mp3")
        elif (current_time.hour >= 12) and (current_time.hour < 18):
            playsound(r"audio\Good_evening.mp3")
        elif (current_time.hour >= 18) and (current_time.hour < 23):
            playsound(r"audio\Good_afternoon.mp3")
        else:
            playsound(r"audio\Greetings_at_night.mp3")

    @staticmethod
    def bye():
        playsound("audio/Goodbye.mp3")
        exit(0)
