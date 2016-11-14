#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import requests
import io
import copy
import yaml
import threading
#from utils import *

CONFIG_FILE = "conf.yaml"

def load_json(filename):
        try:
                data = json.load(open(filename))
        except:
                return None

        return data


img0 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u"       ║   █", 
                u"       ║   ", 
                u"       ║   ", 
                u"       ║   ",
                u"─────╨─────" ]


img1 = [u" ╔═══╦══╗", 
                u" ║    ║   █",
                u" ▒    ║   █", 
                u"       ║   ", 
                u"       ║   ", 
                u"       ║   ",
                u"─────╨─────" ]


img2 = [u" ╔═══╦══╗", 
                u" ║    ║   █",
                u" ▒    ║   █", 
                u" ▐    ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]

img3 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐     ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]
img4 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]
img5 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u" /      ║   ",
                u"─────╨─────" ]
img6 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u" / \    ║   ",
                u"─────╨─────" ]

images = [img0, img1, img2, img3, img4, img5, img6]

import random

class Processor:
    def __init__(self, vkuser):
        self.exclusive = True
        self.config = yaml.load(open(vkuser.module_file("hangman", CONFIG_FILE)))
        self.user = vkuser    
        self.game_context = {"word":self.load_random_word(), "opened": [], "errors":[], "session_started":False }
        self.lock = threading.Lock()


    def load_random_word(self):
        lines = open(self.user.module_file("hangman", self.config["regular_dict"])).readlines()
        lines = [ l.decode("utf-8")[:-2] for l in lines ]
        
        slines = open(self.user.module_file("hangman", self.config["secret_dict"])).readlines()
        slines = [ l.decode("utf-8")[:-2] for l in slines ]
        
        a = lines
        if random.randint(0,100) < 20:
            a = slines

        return a[random.randint(0,len(a)-1)];

    def fail_text(self):
        return random.choice(self.config["fails"])


    def win_text(self):
        return random.choice(self.config["success"])


    def save_context(self, cid):
        with io.open("./files/hangman_{}.context".format(cid), 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(self.game_context, ensure_ascii=False,indent=4, separators=(',', ': '))))

    def load_context(self, cid):
        self.game_context = load_json("./files/hangman_{}.context".format(cid))
        if not self.game_context: 
            self.game_context = {"word":self.load_random_word(), "opened": [], "errors":[], "session_started":False }

    def generate_message(self):
        print self.game_context
        print self.game_context["word"]
        imgp = len(self.game_context["errors"])

        if imgp >= len(images):
                imgp = len(images)-1

        img = copy.copy(images[imgp])

        img[3] += u" Слово: "

        for l in self.game_context["word"]:
                if l in self.game_context["opened"]:
                        img[3] += l + u" "
                else:
                        img[3] += u"_ "


        img[3] += u"("+str(len(self.game_context["word"]))+u")"
        img[4] += u" Ошибки: "
        img[4] += u", ".join(self.game_context["errors"])

        if self.is_end():
            if self.is_win():
                img[6] +=  u"\n" + self.win_text()
            else:
                img[6] +=  u"\n" +  self.fail_text() + u"\nСлово: " + self.game_context["word"]

        return "\n".join(img).replace(' ',"&#8194;");

    def process_message(self, message, chatid, userid):
       
        self.lock.acquire()
        self.load_context(chatid or userid)
        message_body = message["body"].lower().strip()

        if message_body.startswith(self.config["react_on"]):
            self.game_context = {"word" : self.load_random_word(), "opened": [], "errors":[], "session_started" : True }
            self.save_context(chatid or userid)
        
            self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)
            self.lock.release()
            return True

        if not self.game_context["session_started"]:
                self.lock.release()
                return

        if message_body.startswith(u"слово"):

            word = message_body[len(u"слово"):].strip();

            self.open_word(word)
            self.save_context(chatid or userid)

            self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)
            self.lock.release()
            return True

        if not message_body.startswith(u"буква"):
            self.lock.release()
            return

        letter = message_body[len(u"буква"):].strip()[0]

        self.open_letter(letter)
        self.save_context(chatid or userid)
        self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)
        self.lock.release()
        return True

    def open_word(self,word):
    
        if word == self.game_context["word"]:

            self.game_context["opened"].extend([w for w in word])
            self.game_context["opened"] = list(set(self.game_context["opened"]))
            if self.is_end():
                self.game_context["session_started"] = False;
        else:
            self.game_context["errors"].extend([w for w in word])

        
    def open_letter(self,letter):
        if letter in self.game_context["word"]:
            self.game_context["opened"].append(letter)
        else:
            self.game_context["errors"].append(letter)
            self.game_context["errors"] = list(set(self.game_context["errors"]))

        if self.is_end():
                self.game_context["session_started"] = False;
            

    def is_end(self):
        if len(self.game_context["errors"]) >= 6:
            return True
        
        return self.is_win()

        
    def is_win(self):
        for l in self.game_context["word"]:
            if l not in self.game_context["opened"]:
                return False
        return True;
