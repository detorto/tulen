#!/usr/bin/python
# -*- coding: utf-8 -*-

import  urllib
import requests
import time
import urlparse
import sys
import random

from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os

from apscheduler.schedulers.background import BackgroundScheduler
MAX_IMAGES = 15
CURRENT_IMAGE=0

from twill import get_browser
b = get_browser()

from twill.commands import *


session = requests.Session()


def get_new_file_path():
    global MAX_IMAGES
    global CURRENT_IMAGE
        
    CURRENT_IMAGE += 1;
    CURRENT_IMAGE = CURRENT_IMAGE%MAX_IMAGES
    
    return "./files/google_image{}.jpg".format(CURRENT_IMAGE)


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

def download_image(url,filename):
    req = urllib2.Request(url, None, headers)
    raw_img = urllib2.urlopen(req).read()
    f = open(filename, 'wb')
    f.write(raw_img)
    f.close()
    return filename

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
           'Accept':'*/*'}
add_extra_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; rv:10.0) Gecko/20100101 Firefox/10.0")
        
def get_soup(srch):
        
        def make_soup(url):
                go(url)
                page = b.get_html()
                return BeautifulSoup(page,"html.parser")
        
        query = urllib.urlencode(encoded_dict({"text":srch}))
        url="https://yandex.ru/images/search?"+query

        
        soup = make_soup(url)
        return soup

def isBanned(soup):
    
    t = soup.find_all("title")[0].string
    
    if len(t) == 5 and t[-1]=="!":
       print "Banned"
       return True

def get_random_image(soup):
    a =  soup.find_all("a",{"class":"gallery__item carousel__item"})
    if len(a) == 0:
        return None

    h = random.choice(a);
    h = h.get("href")
    parsed = urlparse.urlparse(h)
    image = urlparse.parse_qs(parsed.query)['img_url'][0]
    
    return download_image(image, get_new_file_path())

class Processor:

    def __init__(self,  user):
        self.banned = False
        self.user = user

    def getCaptchaImage(self, soup):
        i = soup.find("img", { "class" : "form__captcha" })
        url= i.get("src")
        return download_image(url, get_new_file_path()) 
    
    def postCaptcha(self,req):
        rep = b.get_form_field(b.get_all_forms()[0],"0").value
        key = b.get_form_field(b.get_all_forms()[0],"1").value
        retpath = b.get_form_field(b.get_all_forms()[0],"2").value

        url = "https://yandex.ru/checkcaptcha?"

        getVars = {'key': key, "rep": req, "retpath":retpath }
        print "Posting captha:", url + urllib.urlencode(encoded_dict(getVars))
        go(url + urllib.urlencode(encoded_dict(getVars)))


    
    def process_message(self, message, chatid, userid):
        if u".jpg" in message["body"].lower() or u".жпг" in message["body"].lower():
            try:
                req = message["body"][:message["body"].lower().index(u".jpg")]
            except:
                req = message["body"][:message["body"].lower().index(u".жпг")]

            if self.banned:
                print "-------POST CAPTHCA"
                self.postCaptcha(req)
                req = self.prev_req

            html = get_soup(req)    
            if isBanned(html):
                print "-------BANNDED"
                self.banned = True
                img = self.getCaptchaImage(html)
                msg_attachments = self.user.upload_images_files([img,])
                self.prev_req = req;
                self.user.send_message(text=u"Помогите разгадать, меня забанили. Ответьте капча_с_картинки.жпг", attachments = msg_attachments, chatid = chatid, userid=userid)
                
                return
            else:                        
                img = get_random_image(html)
                print "-------NOT BANNED"
                self.banned = False;

            if not img:
                self.user.send_message(text=u"Уупс, не нашлось ничего на \""+req+"\"", chatid = chatid, userid=userid)
                return
            print "Uploading imgs"
            msg_attachments = self.user.upload_images_files([img,])
           
            if not msg_attachments:
                self.user.send_message(text=u"Странные же вы, такую хуйню ищите", chatid=chatid, userid=userid)
                return
            self.user.send_message(text=u"["+req+"]", attachments = msg_attachments, chatid = chatid, userid=userid)
            
            wall_attachments = self.user.upload_images_files_wall([img,])
            if not wall_attachments:
                print "Error in wall attachments"
                return
            self.user.post(text=u"["+req+"]", attachments = wall_attachments, chatid = chatid, userid=userid)




if __name__ == "__main__":
        import sys
        html = get_soup("hui")
        if isBanned(html):
           print "banned"
        else:
            img = get_random_image(html)

        print img
