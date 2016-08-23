#!/usr/bin/python
# -*- coding: utf-8 -*-


import  urllib
import requests
import time


class Processor:

	def __init__(self, user):
		self.user = user

	def process_message(self, message, chatid, userid):
		if u".mp3" in message["body"].lower() or u".мп3" in message["body"].lower():

			try:
				req = message["body"][:message["body"].lower().index(u".mp3")]
			except:
				req = message["body"][:message["body"].lower().index(u".мп3")]

			attachment = self.user.find_audio(req)

			if not attachment:
				self.user.send_message( text=u"Уупс, не нашлось ничего на \""+req+"\"", chatid=chatid, userid=userid)
				return
			self.user.send_message(text="["+req+"]",chatid=chatid, userid=userid, attachments=attachment)
			self.user.post(text="["+req+"]",chatid=chatid, userid=userid, attachments=attachment)




