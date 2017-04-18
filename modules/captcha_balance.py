#!/usr/bin/python
# -*- coding: utf-8 -*-


import  urllib
import requests
import time
import vkrequest
from twocaptchaapi import TwoCaptchaApi




class Processor:

	def __init__(self, user):
		pass

	def process_message(self, message, chatid, userid):
		if "captchabalance" in message["body"].lower():
			balance = vkrequest.captcha.balance()
			self.user.send_message( text=u"Баланс на каптчарешателе: {}$. В день решается около 300 каптч, 1000 каптч стоит 1$. На сколько этого хватит - посчитаете сами.".format(balance), chatid=chatid, userid=userid)




