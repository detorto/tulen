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
        self.config = yaml.load(open(vkuser.module_file("censor", CONFIG_FILE)))
        self.exclusive = True

        self.cens_dict = [l.decode("utf8").strip() for l in open(self.user.module_file("censor", self.config["cens_dict"])).readlines()]
        self.reps = [l.decode("utf8").strip() for l in open(self.user.module_file("censor", self.config["repl_dict"])).readlines() ]
        print self.cens_dict

    def process_message(self, message, chatid, userid):

        self.cens_dict = [l.decode("utf8").strip() for l in open(self.user.module_file("censor", self.config["cens_dict"])).readlines()]
	
	
        for word in self.cens_dict:
         
            message_body = message["body"].lower()

            if word in message_body:
                self.user.send_message(text = random.choice(self.reps), chatid=chatid, userid=userid)
		return True
            
