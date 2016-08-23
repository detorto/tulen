#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import yaml
CONFIG_FILE = "conf.yaml"
class Processor:

    def __init__(self, vkuser):
        self.config = yaml.load(open(vkuser.module_file("reply", CONFIG_FILE)))
        self.user = vkuser

    def process_message(self, message, chatid, userid):
        
        message_body = message["body"]
        message_body_low = message_body.lower()
        
        for word in self.config["regexps"].keys():
            
            prog = re.compile(word,flags=re.IGNORECASE| re.UNICODE) 
            if prog.match(message_body):
                self.user.send_message(text = self.config["regexps"][word], chatid=chatid, userid=userid)
                
                
        for word in self.config["in_lines"].keys():
                
                if word == message_body_low:
                    self.user.send_message(text = self.config["in_lines"][word], chatid=chatid, userid=userid)

                if message_body_low.endswith(u" "+word):
                    self.user.send_message(text = self.config["in_lines"][word], chatid=chatid, userid=userid)

