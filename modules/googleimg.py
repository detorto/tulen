#!/usr/bin/python
# -*- coding: utf-8 -*-

import  urllib
import requests
import time
import urlparse
import sys
import random
MAX_IMAGES = 15
CURRENT_IMAGE=0
def get_new_file_path():
	global MAX_IMAGES
	global CURRENT_IMAGE
		
	CURRENT_IMAGE += 1;
	CURRENT_IMAGE = CURRENT_IMAGE%MAX_IMAGES
	
	return "./files/google_image{}.jpg".format(CURRENT_IMAGE)

from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
	
def get_image(srch):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.3',
                'Accept':'*/*'}

	def get_soup(url):
		page = requests.get(url, headers=headers).text
		print page
		return BeautifulSoup(page,"html.parser")
	
	query = urllib.urlencode(encoded_dict({"text":srch}))
	url="https://yandex.ru/images/search?"+query
	
	print url
	soup = get_soup(url)

	def get_image_url(i):
	
		a =  soup.find_all("a",{"class":"gallery__item carousel__item"})
#		a =  soup.find_all("a",{"class":"carousel__item"})

		print "Found ",len(a), "images";	
		sz = 10
		if len(a) < sz:
			sz = len(a)
		i = random.randint(0, sz)
		print "Getting ",i,"image";
		h = a[i].get("href")
		print "href: ",h
	        parsed = urlparse.urlparse(h)
        	
		image = urlparse.parse_qs(parsed.query)['img_url'][0]
	
		return image

	imgurl = None
	try:
		print "getting i"
		imgurl = 	get_image_url(0)
	except:
		e = sys.exc_info()[0]
		print e

	req = urllib2.Request(imgurl, None, headers)
	
	raw_img = urllib2.urlopen(req).read()
	path = get_new_file_path()
	f = open(path, 'wb')
	f.write(raw_img)
	f.close()
	return path

class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user

	def process_message(self, message, chatid, userid):
		if u".jpg" in message["body"].lower() or u".жпг" in message["body"].lower():
			try:
				req = message["body"][:message["body"].lower().index(u".jpg")]
			except:
				req = message["body"][:message["body"].lower().index(u".жпг")]
			print "GOOGLEIMG",req
			img = get_image(req)
			if not img:
				self.user.send_message(text=u"Уупс, не нашлось ничего на \""+req+"\"", chatid = chatid, userid=userid)
				return

			attachments = self.user.upload_images_files([img,])
			if not attachments:
				self.user.send_message(text=u"Странные же вы, такую хуйню ищите", chatid=chatid, userid=userid)
				return

			self.user.send_message(text=u"["+req+"]", attachments = attachments, chatid = chatid, userid=userid)





if __name__ == "__main__":
	import sys
	print get_image(sys.argv[0]) 
