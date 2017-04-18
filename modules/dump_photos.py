#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os
import utils
import urllib
import multiprocessing
import logging 
import os.path
import vkrequest

logger = logging.getLogger("tulen.dump_photos")

CONFIG_FILE = "conf.yaml"

def save_msg(msg, uid):
    if msg["user_id"] != uid and not msg.get("chat_id",None):

        attachments = msg.get("attachments",[])
        for a in attachments:
            if a["type"] == "photo":
                
                logger.info("dumping private photo {}_{}.jpg".format(msg["user_id"],msg["id"]))
                urllib.urlretrieve(a["photo"]["photo_604"], "./files/pphotos/{}_{}.jpg".format(msg["user_id"],msg["id"]))



def first_run_process(api, uid):
    if os.path.isfile("./files/pphotos/finish"):
        return
    offset = 311600
    while True:

        logger.debug("dumping photo offset:  {}".format(offset))
        
        op = api.messages.get
        args = {"count": 200, "offset":offset}
        try:
            messages = vkrequest.perform(op, args)["items"]
        except:
            continue
        if len(messages) == 0:
            f = open("./files/pphotos/finish","wb");
            f.write("asd");
            f.close()
            return 
        [save_msg(m,uid) for m in messages]
        offset += 200


class Processor:
    def __init__(self, vkuser):
        self.user = vkuser
        p = multiprocessing.Process(target=first_run_process, args=(self.user.api,self.user.config["access_token"]["user_id"]))   
        p.start()
    def process_message(self, message, chatid, userid):
        save_msg(message,self.user.config["access_token"]["user_id"])