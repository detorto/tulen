#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os

CONFIG_FILE = "conf.yaml"

class UserStat:
    def __init__(self, uid, warning_limit, ban_limit, decrement):
        self.uid = uid
        self.last_message = u""
        self.counter = 0
        self.warning_limit = warning_limit
        self.ban_limit = ban_limit
        self.decrement = decrement

    def update(self, message):
        if self.last_message == message and message != u"":
            self.counter += 1
        else:
            self.counter -= self.decrement
        if self.counter < 0:
            self.counter  = 0
        self.last_message = message

    def need_warning(self):
        if self.counter == self.warning_limit:
            return True
        return False

    def need_ban(self):
        if self.counter >= self.ban_limit:
            return True
        return False

class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        self.config = yaml.load(open(vkuser.module_file("blacklist", CONFIG_FILE)))
        self.exclusive = True
        self.user_stats = {}

    def save(self):
        with open(self.user.module_file("blacklist", self.config["blacklist"]),"w") as f:
            f.write("\n".join([str(u) for u in self.uids]))

    def block(self, uid):
        self.uids.append(int(uid))
        self.user.send_message(text=self.config["ban_message"], userid=uid)
        self.save()

    def process_message(self, message, chatid, userid):
                    
            self.uids = [int(l.decode("utf8").strip()) for l in open(self.user.module_file("blacklist", self.config["blacklist"])).readlines()]

            msg_uid = int(message["user_id"])
            msg_body = message["body"]

            if msg_body.lower() in self.config["stopwords"]:
                 self.block(msg_uid)
                 return True;
            
            if userid == self.config["master_uid"]:
                if u"блок" in msg_body:
                    self.block(int(msg_body.split()[1]))
                if u"ремув" in message["body"]:
                    self.uids.remove(int(msg_body.split()[1]))
                    self.save()

            if msg_uid in self.uids:
                return True

            user_stat = self.user_stats.get(msg_uid, UserStat(msg_uid, self.config["warning_limit"], self.config["ban_limit"], self.config["decrement"]))
            user_stat.update(msg_body)

            if user_stat.need_warning():
                msg = self.config["warning_message"]
                self.user.send_message(text = msg, userid = userid, chatid = chatid)

            if user_stat.need_ban():
                self.block(msg_uid)
                
                msg = u"Ban for [{}] for [{}]".format(message["user_id"],message["body"])
                self.user.send_message(text = msg, userid = self.config["master_uid"])

                user_stat.counter = 0
                self.user_stats[msg_uid] = user_stat
                return True
            
            self.user_stats[msg_uid] = user_stat
