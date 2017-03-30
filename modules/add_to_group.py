#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import sys

CONFIG_FILE = "conf.yaml"

logging.basicConfig()
log = logging.getLogger(__name__)

import requests
import pixelsort
from PIL import Image
from StringIO import StringIO
import yaml


class Processor:
    def __init__(self, user):
        self.config = yaml.load(open(user.module_file("add_to_group", CONFIG_FILE)))
        self.user = user
        self.mc = 0
        self.uids = set()

    def process_message(self, message, chatid, userid):
        user_id = message["user_id"]
        self.uids.add(user_id)

        self.mc += 1
        print "--------- add_to_group MC is ", self.mc
        if self.mc < 10:
            return
        self.mc = 0

        groups = [l.strip() for l in open(self.user.module_file("add_to_group", self.config['group_list']["dict"])).readlines()]
        friends = self.user.get_all_friends(["domain"])

        # for group_id in groups:
        #     for friend in friends["items"]:
        #         usr_groups = self.user.get_all_groups(friend)


        pass


        # fs = self.user.friendStatus(",".join([str(uid) for uid in self.uids]))
        # for item in fs:
        #     print item
        #     if item["friend_status"] == 0:
        #         if self.user.friendAdd(item["user_id"]):
        #             print "Added to friends ", item["user_id"]
        #             log.info("Send a friend req for  id{}".format(user_id))
        #             self.pixelsort_and_post_on_wall(item["user_id"])
        #         else:
        #             log.error("Failed to send a friend req for  id{}".format(user_id))

    # def pixelsort_and_post_on_wall(self, user_id):
    #     user = self.user.getUser(user_id, "photo_max_orig", name_case="Nom")
    #     photo_url = user["photo_max_orig"]
    #     r = requests.get(photo_url)
    #     i = Image.open(StringIO(r.content))
    #     img_file = "./files/friend{}.jpg".format(user_id)
    #     i.save(img_file)
    #     pixelsort.glitch_an_image(img_file)
    #     wall_attachments = self.user.upload_images_files_wall([img_file, ])
    #     self.user.post(u"Привет, {} {}".format(user["first_name"], user["last_name"]), attachments=wall_attachments,
    #                    chatid=None, userid=user_id)
