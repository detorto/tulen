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
            self.user.send_sticker(userid, userid, chatid)
        self.user.send_message(text=rep, chatid=chatid, userid=userid)

    def process_message(self, message, chatid, userid):
        if chatid == None:
            self.respond(random.choice(self.config.keys()), chatid, userid)

        for word in self.config.keys():

            message_body = message["body"].lower()

            prog = re.compile(word)

            if prog.match(message_body):
                self.respond(word, chatid, userid)
