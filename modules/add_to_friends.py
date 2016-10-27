#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import sys
logging.basicConfig
log = logging.getLogger(__name__)

class Processor:

	def __init__(self , user):
		self.user = user
		
	def process_message(self, message, chatid, userid):
		user_id = message["user_id"]
		fs = self.user.friendStatus(user_id)
		print "UID", user_id, "FS: ", fs
		log.info("UID {} is friend status = {}".format(user_id,fs))
		if fs == 0:
			if self.user.friendAdd(user_id):
				log.info("Send a friend req for  id{}".format(user_id))
			else:
				log.error("Failed to send a friend req for  id{}".format(user_id))


