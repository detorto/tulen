#!/usr/bin/python
# -*- coding: utf-8 -*-

import  urllib
import requests
import time
import json
import random
import re
class Processor:

	def __init__(self, config, user):
		self.config = config
		self.user = user

	def process_message(self, message, chatid, userid):
		if u"тыц" in message["body"]:
                        urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
                        response = urllib.urlopen("http://2ch.hk/b/threads.json")
                        d = response.read()
                        
                        data = json.loads(d.decode('latin-1').encode("utf-8"))
                        print data
                        i = random.randint(0,len(data["threads"]))
                        num = data["threads"][i]["num"]
                        print "http://2ch.hk/b/res/{}.json".format(num)
                        response = urllib.urlopen("http://2ch.hk/b/res/{}.json".format(num))
                        data = json.loads(response.read())
                        i = random.randint(0,data["posts_count"])
                        print data["threads"][0]["posts"][i]
                        text = data["threads"][0]["posts"][i]["comment"]
			attachments=None
			if data["threads"][0]["posts"][i]["files"]:
	                        image = "http://2ch.hk/b/"+data["threads"][0]["posts"][i]["files"][0]["path"]
        	                print urllib.urlretrieve(image, "./files/img.jpg")
                	        attachments = self.user.upload_images_files(["./files/img.jpg",])

			def process_match(m):
			    # Process the match here.
			    return ''
			p = re.compile("<a.*>.*</a>")
			text = p.sub(process_match, text)
                        self.user.send_message(text=text, chatid=chatid, userid=userid, attachments = attachments)



if __name__ == "__main__":
	import sys
	print Processor("","").process_message({"body":sys.argv[1]},0,0)

