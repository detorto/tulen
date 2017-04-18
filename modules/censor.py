#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os
import re
import random

CONFIG_FILE = "conf.yaml"


class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        self.config = yaml.load(open(vkuser.module_file("censor", CONFIG_FILE)))
        self.exclusive = True


    def process_message(self, message, chatid, userid):

        for group in self.config:
            cens_dict = [l.strip() for l in open(self.user.module_file("censor", self.config[group]["cens_dict"])).readlines()]
            reps = [l.strip() for l in open(self.user.module_file("censor", self.config[group]["repl_dict"])).readlines() ]
            regexp = self.config[group]["regexp"]
            if not regexp:
                for word in cens_dict:
                 
                    message_body = message["body"].lower()

                    if word in message_body:
                        self.user.send_message(text = random.choice(reps), chatid=chatid, userid=userid)
                        return True
            else:
                for word in cens_dict:
                 
                    message_body = message["body"].lower()
                    prog = re.compile(word)

                    if prog.match(message_body):
                        self.user.send_message(text = random.choice(reps), chatid=chatid, userid=userid)
                        return True

        return False
            
