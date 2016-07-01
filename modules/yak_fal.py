#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user
		self.counter = 0

	def process_message(self, message, chatid, userid):
		if message["user_id"] == 5319601:
			print "Fal counter: ", self.counter
			self.counter += 1;
		if self.counter % 15 == 0:
			self.counter+=1;
			self.user.send_message(text=u"Фу фал",chatid = chatid, userid = userid )
