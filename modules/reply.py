#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user

	def process_message(self, message, chatid, userid):
		if "words" not in self.config:
			return
		for word in self.config["words"]:
			message_body = message["body"]
		
			

			if "regexp" in self.config["words"][word]:
				if self.config["words"][word]["regexp"]==True:
					prog = re.compile(word,flags=re.IGNORECASE| re.UNICODE)
					#print "regexp is",word
				  	if prog.match(message_body):
				  		self.user.send_message(text = self.config["words"][word]["answer"], chatid=chatid, userid=userid)
						return
					else:
						print message_body, "does not contains", word	

			else:
				
                	        message_body = message_body.lower()
        	                word = word.lower()
	
				if word == message_body:
					self.user.send_message(text = self.config["words"][word]["answer"], chatid=chatid, userid=userid)

				if message_body.endswith(u" "+word):
					self.user.send_message(text = self.config["words"][word]["answer"], chatid=chatid, userid=userid)

