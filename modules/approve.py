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
		
		for word in self.config["react_on"]:
	
			message_body = message["body"].lower()

			prog = re.compile(word)

			if prog.match(message_body):
				reps = [l.strip() for l in open(vkuser.module_file("approve", self.config["dict"])).readlines()]
				rep = random.choice(reps)			
				self.user.send_message(text = rep, chatid=chatid, userid=userid)
