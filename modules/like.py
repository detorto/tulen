#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
from apscheduler.schedulers.background import BackgroundScheduler

class Processor:

	def like_wall(self):
		news = user.get_news()
		for n in news:
			likes = n.get("likes",None)
			if likes and likes["user_likes"] == 0 and likes["can_like"] == 1:
				user.like_post(n["post_id"])

	def __init__(self, config, user):
		self.config = config
		self.user = user
		self.shced  = BackgroundScheduler()
		self.shced.add_job(like_wall, "interval", minutes=1);
		self.shced.start()


	def process_message(self, message, chatid, userid):
		return;