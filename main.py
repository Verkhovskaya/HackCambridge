from __future__ import print_function
import readchar
from azure_translate_api import translate
import serial
import sys
import time
import os
import io
reload(sys)
import time
sys.setdefaultencoding('utf8')


import serial.tools.list_ports

azure_language_code = {
    "Afrikaans": "af",
    "Cantonese": "yue",
    "Catalan": "ca",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Hindi": "hi",
    "Hungarian": "hi",
    "Icelandic": "is",
    "Indonesian": "id",
    "Italian": "it",
    "Latvian": "lv",
    "Mandarin": "zh-Hans", #  simplified
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian": "sr-Latn", #  latin
    "Slovak": "sk",
    "Spanish": "es",
    "Swedish": "sv",
    "Tamil": "ta",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Welsh": "cy"
}

tts_language_code = {
    "Afrikaans": "af",
    "Cantonese": "zh-yue",
    "Catalan": "ca",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",
    "Hindi": "hi",
    "Hungarian": "hi",
    "Icelandic": "is",
    "Indonesian": "id",
    "Italian": "it",
    "Latvian": "lv",
    "Mandarin": "zh", #  simplified
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian": "sr", #  latin
    "Slovak": "sk",
    "Spanish": "es",
    "Swedish": "sv",
    "Tamil": "ta",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Welsh": "cy"
}

#  Tested languages: "no",
language = "Norwegian"
use_glove = True
debug = False


keymap = {
    'a': ['q', 'a', 'z'],
    's': ['w', 's', 'x'],
    'd': ['e', 'd', 'c'],
    'f': ['r', 'f', 'v', 't', 'g', 'b'],
    'j': ['y', 'h', 'n', 'u', 'j', 'm'],
    'k': ['i', 'k', ','],
    'l': ['o', 'l', '.'],
    ';': ['p']
}

loaded_words = []
word_order = {}


def get_modem_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "ARDUINO" in str(p):
            port = str(p).split(" ")[0]
            return port

def text_to_speech(sentence):
    language_code = tts_language_code[language]
    tts_file = open("tts.txt", "w")
    tts_file.write(sentence.encode('utf-8'))
    tts_file.close()
    print('speak -v' + language_code + ' -ftts.txt')
    os.system('speak -v' + language_code + ' "' + sentence + '"')
    pass


def get_word_order(x):
    if x in word_order:
        return word_order[x]
    else:
        print("missing " + x)
        return 0


def match_to_typed(input_word):
    words_considered = filter(lambda x: len(x) >= len(input_word), loaded_words)

    for i in range(len(input_word)):
        words_that_dont_match = []
        for word in words_considered:
            if not word[i] in keymap[input_word[i]]:
                words_that_dont_match.append(word)
        for word in words_that_dont_match:
            words_considered.remove(word)

    words_considered.sort(key=get_word_order)
    words_considered.sort(key=len)

    return words_considered


def load_all_words():
    global loaded_words
    global word_order

    words_file = open("words.txt")
    words = words_file.read().split("\n")[:5000]
    sorted_words = [] # [x.split("\t")[0].lower() for x in words]
    words_file.close()
    words_2_file = open("words_2.txt")
    words_2 = [] #  words_2_file.read().split("\n")
    sorted_words_2 = open("words_3.txt").read().split("\n")
    words_all = list(set(sorted_words).union(set(words_2)).union(set(sorted_words_2)))


    i = 1
    for word in sorted_words_2:
        word_order[word] = i
        i += 1

    loaded_words = words_all

def to_ipa(sentence, language):
    return sentence

load_all_words()

right_fingers = {1: 'j', 2: 'k', 3: 'l', 4: ';'}
left_fingers = {1: 'f', 2: 'd', 3: 's', 4: 'a'}

class GloveInterface:
    def __init__(self):
        #  thumb, pointer, middle, ring, little
        self.received_word = ""
        self.received_sentence = ""
        self.isThumbPressed = False
        self.thumbPressedAlone = False
        self.state = "receiving_characters"
        self.lastCharacterWasSpace = False
        self.word_options = []
        self.chosen_word_id = 0
        self.startTime = 0

    def press_thumb(self):
        if debug:
            print()
            print("Press thumb")
            print("state: " + self.state)
            print()
        self.startTime = time.time()
        self.isThumbPressed = True
        self.thumbPressedAlone = True
        if self.state == "pick_word":
            self.received_sentence += " " + self.word_options[self.chosen_word_id]
            self.state = "exiting_pick_word"
            print()

    def release_thumb(self):
        if debug:
            print()
            print("Release thumb")
            print("state: " + self.state)
            print("lastCharacterWasSpace: " + str(self.lastCharacterWasSpace))
            print("thumbPressedAlone: " + str(self.thumbPressedAlone))
            print()

        self.isThumbPressed = False

        if (time.time() - self.startTime) > 1 and self.thumbPressedAlone:
            self.received_word = ""
            self.word_options = []
            self.state = "receiving_characters"
            self.lastCharacterWasSpace = False
            print()
            print("Clearing. Try again")
            return

        if self.state == "receiving_characters":
            if self.lastCharacterWasSpace:
                print()
                print("Received sentence: " + self.received_sentence)
                if self.received_sentence:
                    translated = translate(self.received_sentence, azure_language_code[language])
                    print("Translated sentence: " + translated)
                    text_to_speech(translated)
                self.received_sentence = ""
            elif self.thumbPressedAlone:
                if not self.word_options:
                    print("No word found matching. Please try again")
                    self.received_word = ""
                    self.lastCharacterWasSpace = True
                else:

                    chosen = str(0)
                    word = self.word_options[0]
                    word_padding = " "*(10-len(self.received_word))
                    options_text = " , ".join(self.word_options[:5])
                    options_text_padding = " "*(50-len(str(options_text)))
                    print(">> chosen {4}: {0} {1}        -> {2} {3}".format(word, word_padding, options_text,
                                                                            options_text_padding, chosen), end="\r")
                    sys.stdout.flush()
                    self.word_options = match_to_typed(self.received_word)
                    self.chosen_word_id = 0
                    if self.word_options:
                        self.state = "pick_word"
                    else:
                        print("No word found matching. Please try again")
                    self.received_word = ""
                    self.lastCharacterWasSpace = True
        elif self.state == "exiting_pick_word":
            self.state = "receiving_characters"


    def press_finger(self, finger_id):
        if debug:
            print()
            print("Press finger")
            print("isThumbPressed: " + str(self.isThumbPressed))
            print()
        self.thumbPressedAlone = False
        self.lastCharacterWasSpace = False
        if self.state == "receiving_characters":
            if self.isThumbPressed:
                self.received_word += left_fingers[finger_id]
            else:
                self.received_word += right_fingers[finger_id]
            self.word_options = match_to_typed(self.received_word)
            word = self.received_word
            word_padding = " "*(10-len(self.received_word))
            options_text = " , ".join(self.word_options[:5])
            options_text_padding = " "*(50-len(str(options_text)))
            print(">> Input word: {0} {1}        -> {2} {3}".format(word, word_padding, options_text, options_text_padding), end="\r")
            sys.stdout.flush()
            if debug:
                print("")
        elif self.state == "pick_word":
            if finger_id == 1:
                self.chosen_word_id = (self.chosen_word_id-1)%5
            elif finger_id == 2:
                self.chosen_word_id = (self.chosen_word_id+1)%5
            elif finger_id == 4:
                print("")
                print("Forgetting word. Enter a new one")
                print(" "*100)
                self.received_word = ""
                self.word_options = []
                self.state = "receiving_characters"
            if self.state != "receiving_characters":
                word = self.word_options[self.chosen_word_id]
            else:
                word = ""
            word_padding = " " * (10 - len(self.received_word))
            options_text = " , ".join(self.word_options[:5])
            options_text_padding = " " * (50 - len(str(options_text)))
            chosen = str(self.chosen_word_id)
            print(">> chosen {4}: {0} {1}        -> {2} {3}".format(word, word_padding, options_text,
                                                                    options_text_padding, chosen), end="\r")
            sys.stdout.flush()

    def release_finger(self, finger_id):
        if debug:
            print()
            print("Release finger")
        if self.state == "receiving_characters":
            pass



glove = GloveInterface()

if use_glove:
    port = get_modem_port()
    if debug:
        print(port)
    if not port:
        raise Exception("Device is being flaky again :(")

    ser = serial.Serial(port, 9600)  # open serial port
    if debug:
        print(ser.name)  # check which port was really used
        print("HELLO")
        print(ser.isOpen())
        print("STARTING PROGRAM")
    while True:
        if not ser.isOpen():
            print("WTFFFF?")
            raise Exception("FUCK THIS SERIAL PORT")
        serial_line = ser.readline().rstrip()
        if debug:
            print(serial_line)

        finger, new_state = serial_line.split(" ")
        finger = int(finger)
        new_state = new_state == '1'

        if finger == 0:
            if new_state == 1:
                glove.press_thumb()
            else:
                glove.release_thumb()
        else:
            if new_state:
                glove.press_finger(finger)
            else:
                glove.release_finger(finger)

else:

    current_state = [False, False, False, False, False]
    while True:
        new_char = readchar.readchar()
        if new_char == 'q':
            break
        elif new_char == " ":
            current_state[0] = not current_state[0]
            if current_state[0]:
                glove.press_thumb()
            else:
                glove.release_thumb()
        elif new_char == 'j':
            current_state[1] = not current_state[1]
            if current_state[1]:
                glove.press_finger(1)
            else:
                glove.release_finger(1)
        elif new_char == 'k':
            current_state[2] = not current_state[2]
            if current_state[2]:
                glove.press_finger(2)
            else:
                glove.release_finger(2)
        elif new_char == 'l':
            current_state[3] = not current_state[3]
            if current_state[3]:
                glove.press_finger(3)
            else:
                glove.release_finger(3)
        elif new_char == ';':
            current_state[4] = not current_state[4]
            if current_state[4]:
                glove.press_finger(4)
            else:
                glove.release_finger(4)