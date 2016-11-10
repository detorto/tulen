#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os

CONFIG_FILE = "conf.yaml"

class Processor:

	def __init__(self,vkuser):
		self.user = vkuser
		self.config = yaml.load(open(vkuser.module_file("approve", CONFIG_FILE)))


	def process_message(self, message, chatid, userid):
		
		for word in self.config.keys():
	
			message_body = message["body"].lower()

			prog = re.compile(word)

			if prog.match(message_body):
				reps = [l.strip() for l in open(self.user.module_file("approve", self.config[word]["dict"])).readlines()]
				rep = random.choice(reps)
				if rep.startswith("img:"):
					print rep
					f = self.user.module_file("approve", rep[rep.rindex("img"):])
					print f
					attc = self.user.upload_images_files([f,])
					self.user.send_message(text = "", attachments = attc, chatid=chatid, userid=userid)
					return
				else:
					self.user.send_message(text = rep, chatid=chatid, userid=userid)
