#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os

CONFIG_FILE = "conf.yaml"

msg = u"""Друге, ты дурак и бан тебе. Если считаешь что не справедливо - иди жалуйся мне на стенку. Иначе - либо донать на каптчу, либо иди нахуй.
Донаты кидать нa QIWI +79166317941 или яды https://money.yandex.ru/to/41001705503465 от 30 рублей, с пометкой "на разбан" и вашим айдишником. 
Все деньги пойдут в сервис решения каптчи 2captcha.com, чтобы тюлень всегда был с вами. C уважением, поддержка."""

class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        self.config = yaml.load(open(vkuser.module_file("blacklist", CONFIG_FILE)))
        self.exclusive = True
        self.block_list = [u"цп.жпг", u"цп.ави",u"цп.гиф"]


    def save(self):
        with open(self.user.module_file("blacklist", self.config["blacklist"]),"w") as f:
            f.write("\n".join([str(u) for u in self.uids]))

    def block(self, uid):
        self.uids.append(int(uid))
        self.user.send_message(text=msg, userid=uid)
        self.save()

    def process_message(self, message, chatid, userid):
 
            self.uids = [int(l.decode("utf8").strip()) for l in open(self.user.module_file("blacklist", self.config["blacklist"])).readlines()]

            print self.uids, message["user_id"],5180483
            if message["body"].lower() in self.block_list:
                 self.block(int(message["user_id"]))
            
            if userid == 5180483:
                print "-------message from master"
                if u"блок" in message["body"]:
                    print "----------block"
                    self.block(int(message["body"].split()[1]))
                if u"ремув" in message["body"]:
                    self.uids.remove(int(message["body"].split()[1]))
                    self.save()

            if message["user_id"] in self.uids:
                return True
