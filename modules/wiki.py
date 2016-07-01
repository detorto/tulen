#!/usr/bin/python
# -*- coding: utf-8 -*-

import wikipedia
import time
import urllib
import requests
import pprint
import json


def get_wiki_page(req):
		wikipedia.set_lang("ru")
		p = wikipedia.page(req)
		return p

IMAGES_COUNT = 3

IMAGES_EXT = (".png",".jpg",".jpeg",".gif",".bmp")

def save_images(page):
	local_images = []
	counter = 0
	for i,img in enumerate(page.images):
		fname = img.split("/")[-1];
		if img.endswith(IMAGES_EXT) and "Aquote" not in fname and "Commons-logo" not in fname and "Wiktionary" not in fname:
			print fname	
			urllib.urlretrieve(img, "./files/"+fname)
			local_images.append("./files/"+fname)
			counter += 1
			if counter >= IMAGES_COUNT:
				break
	return local_images


import time

class Processor:
	
	def __init__(self, config, user):
		self.config = config
		self.user = user

	def process_message(self, message, chatid, userid):

		for word in self.config["react_on"]:
			message_body = message["body"].lower()

			if word in message_body:
				req =message_body[message_body.index(word)+len(word):]
				try:
					p = get_wiki_page(req)
				except:
					text = u"Что то не так. Возможно википедия не знает о \""+req+"\""
					self.user.send_message(text=text, chatid= chatid, userid=userid)
					return 	
			
				files = save_images(p)
				attachments = self.user.upload_images_files(files)

				self.user.send_message(text=p.summary, chatid= chatid, userid=userid, attachments = attachments)
			





