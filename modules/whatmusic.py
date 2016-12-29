#!/usr/bin/python
# -*- coding: utf-8 -*-


import  urllib
import requests
import time
CONFIG_FILE="conf.yaml"

class Processor:

	def __init__(self, user):
		self.user = user
		self.config = yaml.load(open(vkuser.module_file("whatmusic", CONFIG_FILE)))

	def process_message(self, message, chatid, userid):
		for w in self.config["react_on"]:
			if w in message["body"].lower():

			g = random.choice(self.config["groups"])
		
			attachment = self.user.find_audio(g,random=True)

			if not attachment:
				self.user.send_message( text=u"Сорня, не могу сейчас рассказать", chatid=chatid, userid=userid)
				return
			self.user.send_message(text="",chatid=chatid, userid=userid, attachments=attachment)




