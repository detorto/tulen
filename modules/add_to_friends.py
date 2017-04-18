#!/usr/bin/python
# -*- coding: utf-8 -*-
from vk.exceptions import VkAPIError

from threading import Timer
import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import sys

logging.basicConfig
log = logging.getLogger(__name__)
import requests
import pixelsort
from PIL import Image
from  io import StringIO


class Processor:
    def __init__(self, user):
        self.user = user
        self.mc = 0
        self.uids = set()
        self.blocked = False

    def process_message(self, message, chatid, userid):
        user_id = message["user_id"]
        self.uids.add(user_id)
        self.mc += 1
    
        if self.mc < 25:
            return
        self.mc = 0
        uids = self.user.getRequests()
        for uid in uids:
            if self.user.friendAdd(uid):
    
                log.info("Send a friend req for  id{}".format(uid))
                self.pixelsort_and_post_on_wall(uid)

        if self.blocked:
    
            return

        self.mc = 0
        fs = self.user.friendStatus(",".join([str(uid) for uid in self.uids]))
        for item in fs:
    
            if item["friend_status"] == 0:
                try:
                    if self.user.friendAdd(item["user_id"]):
    
                        log.info("Send a friend req for  id{}".format(user_id))
                        self.pixelsort_and_post_on_wall(item["user_id"])
                    else:
                        log.error("Failed to send a friend req for  id{}".format(user_id))
                except VkAPIError as e:
    
                    if e.code != 175 and e.code != 176:
    
                        self.blocked = True
                        t = Timer(60 * 60 * 2, self.unblock, [])
                        t.start()
                        raise

    def unblock(self):
    
        self.blocked = False;
        self.uids = set()
        self.mc = 0

    def pixelsort_and_post_on_wall(self, user_id):
        user = self.user.getUser(user_id, "photo_max_orig", name_case="Nom")
        photo_url = user["photo_max_orig"]
        r = requests.get(photo_url)
        i = Image.open(StringIO(r.content))
        img_file = "./files/friend{}.jpg".format(user_id)
        i.save(img_file)
        pixelsort.glitch_an_image(img_file)
        wall_attachments = self.user.upload_images_files_wall([img_file, ])
        self.user.post(u"Привет, {} {}".format(user["first_name"], user["last_name"]), attachments=wall_attachments,
                       chatid=None, userid=user_id)
