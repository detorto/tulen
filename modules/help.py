#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user
	def isRequest(self,message):
		if message == u"тюлень, что ты умеешь":
			return True
		if message == u"help":
			return True
		if message == u"какие команды ты знаешь?":
			return True
		if message == u"что ты можешь?":
			return True

	def process_message(self, message, chatid, userid):
		message_body = message["body"].lower()
		if self.isRequest(message_body):
			text = u"Могу говорить, могу картинки постить."+"\n";
			text += u"что-то.[jpg|жпг] - случайная картинка из поиска"+"\n"
			text += u"что-то.[mp3|мп3] - случайная аудиозапись из поиска"+"\n"
			text += u"что-то.[avi|ави] - случайная видеозапись из поиска"+"\n"
			text += u"что-то.[gif|гиф] - случайный документ из поиска"+"\n"
			text += u"что-то.[txt|тхт] - случайный коммент из поиска"+"\n"
			text += u"вики:что-то - выжимка из википедии о чем-то"+"\n"
			text += u"повесьте нас - игра висилица, комманды - [буква Х | слово СЛОВО]"+"\n"
			self.user.send_message(text, chatid = chatid, userid = userid)
