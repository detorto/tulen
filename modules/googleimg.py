#!/usr/bin/python
# -*- coding: utf-8 -*-

import  urllib
import urllib2

import requests
import time
import urlparse
import sys
import random
from bs4 import BeautifulSoup
import requests
import re
import tempfile
import os

YANDEX_URL = "https://yandex.ru/images/search?{}"

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
           'Accept':'*/*'}

urllib.URLopener.version  = headers["User-Agent"]

session = requests.Session()
session.headers.update(headers)
cookies = {}
max_file_i = 100
ci = 0
def get_new_file_name():
#    return tempfile._get_candidate_names()
    global ci    
    while True:
        ci += 1
        ci = ci % max_file_i
        yield str(ci)
        

def get_html(url):
    global cookies
    r = session.get(url,cookies=cookies)
    print r.url
    cookies.update(session.cookies.get_dict())
    print cookies
    return r.text

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

def make_soup(query):
    query = urllib.urlencode(encoded_dict({"text":query}))
    page = get_html(YANDEX_URL.format(query))
    return BeautifulSoup(page, "html.parser")

def download_image(url, filename):
    try:
        print "Downloading [{}] to {}".format(url,filename)
        urllib.urlretrieve(url, filename)
        return True
    except: 
        print sys.exc_info()
        return False
    
def isBanned(soup):
    t = soup.find_all("title")[0].string
    
    if len(t) == 5 and t[-1]=="!":
       print "Banned"
       return True

def get_images_urls(soup):
    a =  soup.find_all("a",{"class":"gallery__item carousel__item"})
    if len(a) == 0:
        return []
    images_urls = []
    for img in a:
        h = img.get("href")
        parsed = urlparse.urlparse(h)
        image = urlparse.parse_qs(parsed.query)['img_url'][0]
        images_urls.append(image)
    
    return images_urls

#temp_name = next(tempfile._get_candidate_names())
captcha_text = [u"Такие дела, голуби. Ответьте капча_с_картинки.жпг. КАПЧА_С_КАРТИНКИ.ЖПГ блять, а не просто капча_с_картинки.",
u"Чуваки, яндекс банит меня от зависти. Ответье словом с картинки. СЛОВО_С_КАРТИНКИ.жпг, вот так.", 
u"Чот вы много говна ищите, вот вам капча. Разгадайте за меня. Отвечать нужно КАПЧА_С_КАРТИНКИ.жпг. Только так.",
u"Ну вот, опять. Помогите что-ли, ответьте КАПЧА_С_КАРТИНКИ.жпг",
u"Помогите понять яндексу, что это не я, а вы ищете такую хуйню. Ответьте СЛОВО_С_КАРТИНКИ.жпг"]
class Processor:

    def __init__(self,  user):
        self.banned = False
        self.user = user
        self.chats_know_about_ban = []
        self.prev_req = {}

    def getCaptchaImage(self, soup):
        i = soup.find("img", { "class" : "form__captcha" })
        url= i.get("src")
        
        print soup.find_all("input")
        self.last_key = soup.find("input",{"name":"key"})["value"]
        self.last_retpath = soup.find("input",{"name":"retpath"})["value"]
        fname = "./files/"+next(tempfile._get_candidate_names())+".jpg"
        download_image(url, fname)
        return fname
   
    
    def postCaptcha(self,req):
        #rep = b.get_form_field(b.get_all_forms()[0],"0").value
        #key = b.get_form_field(b.get_all_forms()[0],"1").value
        #retpath = b.get_form_field(b.get_all_forms()[0],"2").value

        url = "https://yandex.ru/checkcaptcha?"
        getVars = {'key': self.last_key, "rep": req, "retpath":self.last_retpath }
        print "Posting captha:", url + urllib.urlencode(encoded_dict(getVars))
        get_html(url + urllib.urlencode(encoded_dict(getVars)))


    def process_message(self, message, chatid, userid):
        global session
        chatid = chatid or userid
        if u".jpg" in message["body"].lower() or u".жпг" in message["body"].lower():
            try:
                req = message["body"][:message["body"].lower().index(u".jpg")]
            except:
                req = message["body"][:message["body"].lower().index(u".жпг")]

            if self.banned:
                if chatid in self.chats_know_about_ban:
                    print "know about ban, post captha"
                    self.postCaptcha(req)
                    self.chats_know_about_ban = []
                    req = self.prev_req[chatid]
                else:
                    msg_attachments = self.user.upload_images_files([self.last_capthca_img,])
                    self.prev_req[chatid] = req;
                    self.user.send_message(text=random.choice(captcha_text), attachments = msg_attachments, chatid = chatid, userid=userid)
                    self.chats_know_about_ban.append(chatid)
                    return

            html = make_soup(req)    
            self.req = req
            if isBanned(html):
                print "-------BANNDED"
                self.banned = True
                
                self.last_capthca_img = self.getCaptchaImage(html)

                msg_attachments = self.user.upload_images_files([self.last_capthca_img,])
                self.prev_req[chatid] = req;
                self.user.send_message(text=random.choice(captcha_text), attachments = msg_attachments, chatid = chatid, userid=userid)
                self.chats_know_about_ban.append(chatid)
                return

            else:                        
                session = requests.Session()
                session.headers.update(headers)
 
                all_images = get_images_urls(html)
                print "-------NOT BANNED", len(all_images)
                if all_images:
                    random_url = random.choice(all_images)

                    imgfilename = "./files/"+next(get_new_file_name())+".jpg"
                    downloaded = download_image(random_url, imgfilename)

                else:
                    downloaded = False

                self.banned = False;
                self.chats_know_about_ban = []
            
            if not downloaded:
                self.user.send_message(text=u"Уупс, не нашлось ничего на \""+req+"\"", chatid = chatid, userid=userid)
                return
            
            print "Uploading imgs",imgfilename
            msg_attachments = self.user.upload_images_files([imgfilename,])
           
            if not msg_attachments:
                self.user.send_message(text=u"Странные же вы, такую хуйню ищите", chatid=chatid, userid=userid)
                return
            self.user.send_message(text=u"["+req+"]", attachments = msg_attachments, chatid = chatid, userid=userid)
            
import multiprocessing
pool = multiprocessing.Pool(1)

if __name__ == "__main__":
        class User():
            def send_message(self, **kwargs):
                print kwargs["text"]
                

            def upload_images_files(self,*args):
                return ["imageatt",]
        reqs = open("../config/hangman/regular_dict.txt").readlines()
        p = Processor(User())
        def do(r):
            message = {"body":"{}.jpg".format(r).decode("utf-8"),"chat_id":0}
            p.process_message(message,0,0)
        pool.map(do,reqs)
            
            
        

