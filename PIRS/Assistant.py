import pyaudio
from datetime import datetime
import webbrowser as wb
from fuzzywuzzy import fuzz
from os import system
from random import choice
from playsound import playsound
from PyQt5 import QtCore
from recognizer import Recognizer

# Phrases
phrases_for_executing = ["Doing.mp3", "Will_be_done.mp3", "How_say_sir.mp3"]
phrases_for_web_search = ["Finding_information 1.mp3", "Finding_information 2.mp3", "Request_accepted.mp3"]
search_tags = ("как", "кто такой", "кто такая", "что такое", "найди", "ищи", "найти")

""" ---> Voice Assistant <--- """


class Assistant(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.rc = Recognizer()
        # default commands of PIRS
        self.tasks = {
            # internet and social networks
            ("открой ютуб", "включи ютуб"): self.youtube,
            ("открой вконтакте", "включи вконтакте"): self.vk,
            # system commands and windows apps
            ("открой диспетчер задач", "запусти диспетчер задач"): self.taskmgr,
            ("открой панель управления", "запусти панель управления"): self.control,
            ("открой проводник", "запусти проводник"): self.explorer,
            ("открой параметры", "запусти параметры"): self.params,
            ("выключи компьютер", "выключи пк"): self.turn_off,
            ("перезагрузи компьютер", "перезагрузи пк"): self.refresh,
            ("открой калькулятор", "запусти калькулятор"): self.calc,
            ("заверши работу",): self.bye
        }
        # dictionary for count of often functions
        self.count = {
            ("открой ютуб", "включи ютуб"): 0,
            ("открой вконтакте", "включи вконтакте"): 0,
            ("открой диспетчер задач", "запусти диспетчер задач"): 0,
            ("открой панель управления", "запусти панель управления"): 0,
            ("открой проводник", "запусти проводник"): 0,
            ("открой параметры", "запусти параметры"): 0,
            ("выключи компьютер", "выключи пк"): 0,
            ("перезагрузи компьютер", "перезагрузи пк"): 0,
            ("открой калькулятор", "запусти калькулятор"): 0,
            ("заверши работу",): 0
        }

    def voice_activation(self):
        while True:
            if self.rc.start():
                self.cmd(self.rc.speech_to_text())

    # commands execution
    def cmd(self, task):
        self.feedDict(self.tasks)         # download commands from txt file
        cmd = self.inaccurateSearch(task) # inaccurate search
        if cmd in self.tasks:
            if isinstance(self.tasks[cmd], str): return self.open_site(self.tasks[cmd])
            else:                                return self.tasks[cmd]()
        elif cmd not in self.tasks:
            for tag in search_tags:
                if tag in task:
                    return self.web_search(task)
        else:
            playsound("audio/Repeat_please.mp3")
            new_task = self.rc.speech_to_text()
            if new_task != "":
                self.cmd(new_task)

    # cashing technology
    def getOftenTask(self):
        max = 0
        cashe = ''
        for key, value in self.count.items():
            if value > max:
                max = value
                cashe = key
        return cashe
        
    def inaccurateSearch(self, task):
        cashe = self.getOftenTask()
        for tsk in cashe:
            if fuzz.ratio(task, tsk) > 90:
                self.count[cashe] += 1
                return cashe                
        cmd = task # command
        max_similar = 0 # the coefficient of similarity
        for tpl in self.tasks:
            for tsk in tpl:
                rate_similar = fuzz.ratio(task, tsk)
                if rate_similar>75 and rate_similar>max_similar:
                    max_similar = rate_similar
                    cmd = tpl
        if cmd!=task:
            self.count[cmd] += 1
        return cmd

    # getting commands from file "command.txt"
    def downloadCommand(self):
        with open("commands.txt") as file:
            for line in file:
                uc = line.replace("\n", "")
                uc = uc.split(";")
                url = uc[0]
                command = (uc[1],)
                self.tasks[command] = url
                self.count[command] = 0

    @staticmethod
    def countFunc():
        with open("commands.txt") as file:
            n = sum(1 for line in file)
        return n

    def feedDict(self, dict):
        count = 10 + self.countFunc()
        if count != len(dict):
            self.downloadCommand()        

    # Choosing random phrase for executing command
    @staticmethod
    def random_phrase(pr_phrase=None):
        phrase_exe = choice(phrases_for_executing)
        if pr_phrase != None:
            phrase = choice([phrase_exe, pr_phrase])
            audio_file = f"audio/{phrase}"
        else:
            audio_file = f"audio/{phrase_exe}"
        playsound(audio_file, block=False)

    @staticmethod
    def random_phrase_web():
        phrase = choice(phrases_for_web_search)
        audio_file = f"audio/{phrase}"
        playsound(audio_file, block=False)

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
    
    def open_site(self, url):
        wb.open(url)
        self.random_phrase("Opening.mp3")

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
            playsound(r"audio/Good_morning.mp3")
        elif (current_time.hour >= 12) and (current_time.hour < 18):
            playsound(r"audio/Good_evening.mp3")
        elif (current_time.hour >= 18) and (current_time.hour < 23):
            playsound(r"audio/Good_afternoon.mp3")
        else:
            playsound(r"audio/Greetings_at_night.mp3")

    @staticmethod
    def bye():
        playsound("audio/Goodbye.mp3")
        exit()