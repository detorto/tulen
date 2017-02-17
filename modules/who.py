#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os
import utils

CONFIG_FILE = "conf.yaml"

triggers = [u"тюлень, кто", 
            u"тюлень кто",
            u"тюля, кто"
            u"тюля кто",
            u"кто",]

class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        self.config = yaml.load(open(vkuser.module_file("who", CONFIG_FILE)))

    def respond(self, chatid, query):
        op = self.user.api.messages.getChatUsers
        args = {"chat_id" :int(chatid),"fields":"photo"}
        
        ret = utils.rated_operation(op, args)
        user = random.choice(ret)
        fname = user["first_name"]
        lname = user["last_name"]

        sentense_start = random.choice(self.config["replies"])

        self.user.send_message(text =  u"{} {} {}".format(sentense_start,fname,lname), chatid=chatid, userid=None)
        
        return True

    def process_message(self, message, chatid, userid):
            message_body = message["body"].lower()

            for t in triggers:
                if message_body.startswith(t):
                    return self.respond(chatid, message_body[len(t):])
