from vosk import Model, KaldiRecognizer
import pyaudio
import json
import struct
from math import sqrt
import time
from PyQt5 import QtCore
from playsound import playsound

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
TIMEOUT_LENGTH = 3
SAMPLE_WIDTH = 2
SHORT_NORMALIZE = 1.0 / 32768.0
Energy_speech = 100
hot_word = 'пирс'


class Recognizer(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.Threshold = 20
        # vosk
        self.model = Model("speech_model")
        self.rec = KaldiRecognizer(self.model, RATE)
        # pyaudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FPB
        )
        self.stream.start_stream()

    # rms(rated maximum sinusoidal) noise calculation
    @staticmethod
    def rms(frame):
        count = len(frame) / SAMPLE_WIDTH
        form = "%dh" % count
        shorts = struct.unpack(form, frame)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = sqrt(sum_squares / count)
        return rms * 1000

    # Automatically adjusts microphone level to the environment
    def adjustment_to_noise(self, duration=1):
        seconds_per_buffer = FPB / RATE
        end_time = 0
        while True:
            end_time += seconds_per_buffer
            if end_time > duration:
                break
            data = self.stream.read(FPB)
            rms = self.rms(data)

            damping = 0.15 ** seconds_per_buffer
            target_rms = rms * 1.5
            self.Threshold = Energy_speech * damping * target_rms * (1 - damping)

    def speech_to_text(self):
        self.adjustment_to_noise()
        task = ''
        now = time.time()
        end = time.time() + TIMEOUT_LENGTH
        while now <= end:
            data = self.stream.read(FPB)
            # checking the ambient volume
            if self.rms(data) >= self.Threshold:
                end = time.time() + TIMEOUT_LENGTH / 1.2
            now = time.time()
            # vosk
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())
                task = text['text']
        return task

    def start(self):
        while True:
            data = self.stream.read(FPB)
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())
                task = text['text']
                if hot_word in task:
                    playsound("audio/Listen_to_you.mp3")
                    return True
