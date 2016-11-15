#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from  StringIO import StringIO
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
				self.pixelsort_and_post_on_wall(user_id)
			else:
				log.error("Failed to send a friend req for  id{}".format(user_id))
	def pixelsort_and_post_on_wall(self, user_id):
		user = self.user.getUser(user_id,"photo_max_orig",name_case="Nom")
		photo_url = user["photo_max_orig"]
		r = requests.get(photo_url)
            	i = Image.open(StringIO(r.content))
		img_file = "./files/friend{}.jpg".format(user_id)
                i.save(img_file)
		pixelsort.glitch_an_image(img_file)	
		wall_attachments = self.user.upload_images_files_wall([img_file,])
	        self.user.post(u"Привет, {} {}".format(user["first_name"],user["last_name"]), attachments = wall_attachments, chatid = None, userid=user_id)






