#!/usr/bin/python
# -*- coding: utf-8 -*-


import  urllib
import requests
import time
from twocaptchaapi import TwoCaptchaApi




class Processor:

	def __init__(self, user):
		self.user = user
		capthca_api_key = self.user.config.get("twocaptcha_api_key", None)
		self.tcapi = None
		if capthca_api_key:
			self.tcapi  = TwoCaptchaApi(capthca_api_key)


	def process_message(self, message, chatid, userid):
		if not self.tcapi:
			return
		if "captchabalance" in message["body"].lower().encode("utf-8"):
			balance = self.tcapi.get_balance()
			self.user.send_message( text=u"Баланс на каптчарешателе: {}$. В день решается около 300 каптч, 1000 каптч стоит 1$. На сколько этого хватит - посчитаете сами.".format(balance), chatid=chatid, userid=userid)




