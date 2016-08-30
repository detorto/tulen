#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
import yaml
import os
from PIL import Image
import requests
from  StringIO import StringIO
import PIL.ImageOps  

class Processor:

    def __init__(self,vkuser):
        self.user = vkuser

    def negate_image(self, img):
	return PIL.ImageOps.invert(img)        
    def poster_image(self,img):
	return PIL.ImageOps.posterize(img, random.randint(1,8))
    def solar_image(self, img):
        return PIL.ImageOps.solarize(img, threshold=random.randint(0,255))
    def process_message(self, message, chatid, userid):
		
        message_body = message["body"].lower()
	try:
            photo_url = message["attachments"][0]["photo"]["photo_604"]
            r = requests.get(photo_url)
            i = Image.open(StringIO(r.content))
        except:
            return
	
        if message_body == u"негатни":
            self.negate_image(i).save("./files/neg.jpg")
            a = u"Негатнул"
	elif message_body == u"постерни":
            self.poster_image(i).save("./files/neg.jpg")
            a = u"Постернул"
	elif message_body == u"соларни":
            self.solar_image(i).save("./files/neg.jpg")
            a = u"Соларнул"
	else:
            return

        msg_attachments = self.user.upload_images_files(["./files/neg.jpg",])

        if not msg_attachments:
            return

        self.user.send_message(text=a, attachments = msg_attachments, chatid = chatid, userid=userid)

        wall_attachments = self.user.upload_images_files_wall(["./files/neg.jpg",])
        if not wall_attachments:
            print "Error in wall attachments"
            return
        self.user.post(a, attachments = wall_attachments, chatid = chatid, userid=userid)
