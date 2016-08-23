#!/usr/bin/python
# -*- coding: utf-8 -*-


import  urllib
import requests
import time


class Processor:

	def __init__(self, user):
		self.user = user

	def process_message(self, message, chatid, userid):
		if u".txt" in message["body"].lower() or u".тхт" in message["body"].lower():

			try:
				req = message["body"][:message["body"].lower().index(u".txt")]
			except:
				req = message["body"][:message["body"].lower().index(u".тхт")]

			attachment = self.user.find_wall(req)

			if not attachment:
				self.user.send_message( text=u"Уупс, не нашлось ничего на \""+req+"\"", chatid=chatid, userid=userid)
				return
			self.user.send_message(text="["+req+"]", chatid=chatid, userid=userid, attachments=attachment)




