#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os

CONFIG_FILE = "conf.yaml"


class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        self.config = yaml.load(open(vkuser.module_file("approve", CONFIG_FILE)))

    def respond(self, word, chatid, userid):
        reps = [l.strip() for l in open(self.user.module_file("approve", self.config[word]["dict"])).readlines()]
        rep = random.choice(reps)
        rand = random.randint(1, 100)
        if 35 <= rand <= 65:
            try:
                self.user.send_sticker(userid, userid, chatid)
            except:
                pass
	
        if rep.startswith("img:"):
            print rep
            f = self.user.module_file("approve", rep[rep.rindex("img"):])
            attc = self.user.upload_images_files([f,])
            self.user.send_message(text = "", attachments = attc, chatid=chatid, userid=userid)
            return
        else:
            self.user.send_message(text=rep, chatid=chatid, userid=userid)

    def process_message(self, message, chatid, userid):
	responded = False

        for word in self.config.keys():
            
            message_body = message["body"].lower()

            prog = re.compile(word)

            if prog.match(message_body):
                self.respond(word, chatid, userid)
                responded = True
            
        if chatid == None and not responded:
            pu_dicts = [k for k in self.config.keys() if self.config[k].get("private_use",False)]
            self.respond(random.choice(pu_dicts), chatid, userid)
            return

