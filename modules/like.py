#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import sys

log = logging.getLogger('tulen')

class Processor:
    def __init__(self, user):
        self.user = user
        self.shced = BackgroundScheduler()
        self.shced.add_job(self.like_wall, "interval", seconds=60)
        self.shced.start()

    def like_wall(self):
        print "Will like a wall!"
        try:
            news = self.user.get_news()

            for n in news:
                likes = n.get("likes", None)
                if likes and likes["user_likes"] == 0 and likes["can_like"] == 1:
                    print "LIKE", n["post_id"]
                    self.user.like_post(n["post_id"], n["source_id"])
        except Exception as e:
            log.error("Wall-like module exception - {}".format(e.message))

    def process_message(self, message, chatid, userid):
        pass
