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

   
def glitch_an_image(local_image):
  files = {'image': open(local_image, 'rb')}
  data= { 'method':'grey',
          'columns': 'on',
          'treshold':random.randint(30,100) }

  r = requests.post("https://glitch-pixelsort.hyperdev.space/", files=files,data=data)
  
  if r.status_code == 200:
    with open(local_image, 'wb') as f:
      for chunk in r:
            f.write(chunk)  

class Processor:

    def __init__(self,vkuser):
        self.user = vkuser

  
    def process_message(self, message, chatid, userid):
        
        message_body = message["body"].lower()
        try:
            photo_url = message["attachments"][0]["photo"]["photo_604"]
            r = requests.get(photo_url)
            i = Image.open(StringIO(r.content))
        except:
            return
    
        if message_body == u"сортани":
                i.save("./files/neg.jpg")
                glitch_an_image("./files/neg.jpg")
                a = u"Сортанул"
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



if __name__ == '__main__':
  import sys
  if len(sys.argv) < 2:
    print "Wrong number of arguments"
    print """  Usage: \
          python filter.py [curvefile] [imagefile] """
  else:


      im = sys.argv[1]

      glitch_an_image(im)
