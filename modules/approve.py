#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user

	def process_message(self, message, chatid, userid):
		if "words" not in self.config:
			return
		for word in self.config["words"]:
			message_body = message["body"].lower()
		
			prog = re.compile(word)
			if prog.match(message_body):
				reps = self.config["words"][word]
				rep = random.choice(reps)			
				self.user.send_message(text = rep, chatid=chatid, userid=userid)
