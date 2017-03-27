#coding: utf-8
import vk
import time
import json
import requests
from utils import *
import utils
import io
import sys
import traceback
from multiprocessing.pool import ThreadPool
import multiprocessing
import os
import logging
import random
import threading

logger = logging.getLogger('tulen')
logger.setLevel(logging.DEBUG)

class VkUser(object):

    def __init__(self, config, update_stat, testmode = False):
	random.seed(time.time())
        self.config = config

        self.update_stat_ = update_stat

        if testmode:
            session = None
            self.api = None
            logger.info("Running in test mode")
        else:
            session = vk.Session(access_token=self.config["access_token"]["value"])
            self.api = vk.API(session,  v='5.50', timeout = 10)
            logger.info("VK API created")

        capthca_api_key = self.config.get("twocaptcha_api_key", None)
        if capthca_api_key:
            init_2captcha(capthca_api_key)
            logger.info("2Captcha initialized. balance: {}".format(utils._2captcha_api.get_balance()))

        run_ratelimit_dispatcher();
        logger.info("Rate-limit dispatcher started");
        

        modules_list_file = self.config.get("enabled_modules_list", None)

        if not modules_list_file:
            mods = self.config.get("enabled_modules", None)
        else:
            mods = [l.strip() for l in open(modules_list_file).readlines()]

        mods = [m for m in mods if not m.startswith("#")]
        if not mods:
            raise RuntimeError("Can't find any module to load!")
        logger.info("Enabled modules: [{}]".format(",".join(mods)))
        
        self.load_modules(mods)

        self.thread_pool_modules = ThreadPool(int(config.get("mod_threads", 4)))
        
        self.message_queue_general = multiprocessing.Queue()
        self.message_queue_parallel = multiprocessing.Queue()

        
        self.mutex = multiprocessing.Lock()
        
        self.testmode = testmode
        self.message_processors_general = [ threading.Thread(target=self.process_message_general) for x in xrange(int(config.get("msg_threads", 4)))]
        self.message_processors_parallel = [ threading.Thread(target=self.process_message_parallel) for x in xrange(int(config.get("mod_threads", 4)))]
        for t in self.message_processors_general:
            t.start()
        for t in self.message_processors_parallel:
            t.start()
        
        logger.info("Multiprocessing intiated: "+str(self.thread_pool_modules) + " "+ str(self.thread_pool_modules))
        


    def load_modules(self, mod_list):
        
        self.unique_modules = []
        self.global_modules = []
        self.parallel_modules = []

        for module in mod_list:
            data = module.split();
            modif = "parallel"
            module = data[0]
            if len(data) > 1:
                 modif = data[0]
                 module = data[1]              
              
            package = __import__("modules"+"."+module)
            processor = getattr(package, module)
            modprocessor = processor.Processor(self)
            if modif == "unique":
                self.unique_modules.append(modprocessor)
            elif  modif == "global":
                self.global_modules.append(modprocessor)
            else:
                self.parallel_modules.append(modprocessor)

            logger.info("Loaded module: [{}] as {}".format("modules"+"."+module, modif))

    def module_file(self,  modname, filename):
        return os.path.join(self.config.get("modules_config_dir", "config"),modname, filename)

    def update_stat(self, stat, value):
        logger.debug("Mutex acuire")
        self.mutex.acquire()
        logger.debug("Mutex acuired")
        self.update_stat_(stat, value)
        self.mutex.release()
        logger.debug("Mutex released")

    def get_all_messages(self):
        logger.debug("Retrieving messages")
        if self.testmode:
            msg = raw_input("msg>> ")
            msg = msg.decode('utf-8')
            messages = [{"read_state":0, "id":"0","body":msg,"chat_id":2}]
        else:
            code = """var k = 200;
var messages = API.messages.get({"count": k});

var ids = "";
var a = k;  
while (a >= 0) 
{ 
ids=ids+messages["items"][a]["id"]+",";
a = a-1;
}; 
ids = ids.substr(0,ids.length-1);
API.messages.markAsRead({"message_ids":ids});

return messages;"""
#            operation = self.api.messages.get
            operation = self.api.execute
            args = {"code" : code}
            ret = rated_operation( operation, args )
            messages = ret["items"]

        return messages
        #self.process_messages(messages)

    def get_all_friends(self, fields):
        logger.debug("Retrieving messages")

        operation = self.api.friends.get
        args = {"fields": fields}
        return rated_operation(operation, args)
   
    def process_message_in_module(self, module, message):
        chatid = message.get("chat_id",None)
        userid = None

        if not chatid:
            userid = message.get("user_id", None)

        return module.process_message(message, chatid, userid)

    def log_exception(self,data):
        logger.error("Something wrong while processin {}".format(str(data)))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        self.update_stat("errors", 1)


    def process_message_general(self):
        while True:
            try:
                message = self.message_queue_general.get()
                logger.debug("General message processing")
                logger.debug("Unique modules:" + str(len(self.unique_modules)))       

                shold_break = False;
                for m in self.unique_modules:
                    if self.process_message_in_module(m, message) == True:
                        logger.info("Unique module {} worked".format( m.__class__))
                        shold_break = True
                        break

                if shold_break:
                    continue

                logger.info("Sending message to parallel modules")
                for i,_ in enumerate(self.parallel_modules):
                    self.message_queue_parallel.put( (message,i) )
            except:
                self.log_exception("general message")


    def process_message_parallel(self):
        while True:
            try:
                message, module_index = self.message_queue_parallel.get()
                logger.debug("Parallel message processing")
                self.process_message_in_module(self.parallel_modules[module_index],message)
            except:
                self.log_exception("parallel processing")            


    def process_messages(self, messages):

        unread_messages = [ msg for msg in messages if msg["read_state"] == 0]
        if len(unread_messages) > 0:
            logger.info("Unread messages: {}".format("\n".join([m["body"].encode("utf8") for m in unread_messages])))

        if len(unread_messages) > 0:
            logger.debug("Processing global-modules messages events")

            for m in unread_messages:
                print "Processing message in global mods: ", len(self.global_modules)
                for mod in self.global_modules:
                    self.process_message_in_module(mod, m)
            
            logger.debug("Sending messages to queue [{}]".format(len(unread_messages)))
            
            for message in unread_messages:
                self.message_queue_general.put(message)

            self.update_stat("processes",len(unread_messages))

    def send_message(self, text="", chatid=None, userid=None, attachments=None):
        try:       
            logger.info("Sending msg [{}] to c[{}]:u[{}] with attachment [{}]".format(text,
                                                                                    chatid,
                                                                                    userid,
                                                                                    repr(attachments)))
        except:
            logger.info("Sending some unformated !!!!! msg to {}:{}".format(chatid,userid))
        if self.testmode:
            print "----",text, attachments
            return 

        if not attachments:
            attachments = {}
            
        op = self.api.messages.send
        try:
            text = text.decode("utf-8")
        except:
            pass
        text = text.replace(u"а",u"a")
        text = text.replace(u"е",u"e")
        text = text.replace(u"о",u"o")
        text = text.replace(u"с",u"c")


        if isinstance(userid, (int, long)):
            args = {"chat_id" :chatid, "user_id" : userid, "message" : text, "attachment" : attachments}
        else:
            args = {"chat_id": chatid, "domain": userid, "message": text, "attachment": attachments}
        args.update({"random_id": random.randint(0xfff, 0xffffff)})
        ret = rated_operation(op, args)
        
        if not ret:
            logger.warning("No answer for operation")

        self.update_stat("send", 1)

    def send_sticker(self, user_id, peer_id, chat_id, sticker_id=0):
        op = self.api.messages.sendSticker
        if isinstance(user_id, (int, long)):
            args = {"user_id": user_id, "peer_id": peer_id, "chat_id": chat_id,
                    "random_id": random.randint(0xfff, 0xffffff),
                    "sticker_id": random.randint(1, 168) if sticker_id == 0 else sticker_id}
        else:
            args = {"domain": user_id, "peer_id": peer_id, "chat_id": chat_id,
                    "random_id": random.randint(0xfff, 0xffffff),
                    "sticker_id": random.randint(1, 168) if sticker_id == 0 else sticker_id}
        ret = rated_operation(op, args)
        if ret == 100 or (900 <= ret <= 902):
            args["random_id"] = random.randint(0xfff, 0xffffff)
            args["sticker_id"] = random.randint(1, 168)
            return rated_operation(op, args)
        return ret

    def post(self, text, chatid, userid, attachments):
	#return None
        oppost = self.api.wall.post
        args = {"owner_id" :int(self.config["access_token"]["user_id"]), "message" : text, "attachments" : ",".join(attachments)}
            
        print "Posting on wall"
        print pretty_dump(args)

        ret = rated_operation(oppost, args)
        
        self.update_stat("attachments", len(attachments))
        self.update_stat("post", 1)
        return ret

    def __upload_images(self, upserver, files):
        photos = []
        for f in files:
            op = requests.post
            args = {"url" : upserver["upload_url"], "files" : {'photo': (f.split("/")[-1], open(f, 'rb'))}}
            try:
                response = op(**args)
                pj =  response.json()
                ph = {"photo":pj["photo"], "server":pj["server"],"hash":pj["hash"]}
                photos.append(ph)
            except:
                print "Error in photo uploading"
        return photos

    def upload_images_files(self, files):
        op = self.api.photos.getMessagesUploadServer
        args = {}
        upserver = rated_operation(op, args)
        print "Got upserver"        
        ids = self.__upload_images(upserver, files)
        print "Uploaded images"
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveMessagesPhoto
                args = {"photo":i["photo"], "server":i["server"], "hash":i["hash"]}

                resp = rated_operation(op, args)
                print "Saved photos"
                print "Uload resp:",resp
                attachments.append("photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:

                print "Error in photo saving:"
                return None

        self.update_stat("images_uploaded", len(attachments))
    
        return attachments

    def upload_images_files_wall(self, files):
        #return [] 
        op = self.api.photos.getWallUploadServer
        args = {"group_id":int(self.config["access_token"]["user_id"])}
        upserver = rated_operation(op, args)

        photos = self.__upload_images(upserver,files)
        
        ids = photos
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveWallPhoto
                args = {"user_id":int(self.config["access_token"]["user_id"]),"group_id":int(self.config["access_token"]["user_id"]), "photo":i["photo"], "server":i["server"], "hash":i["hash"]}

                resp = rated_operation(op, args)
        
                attachments.append("photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:
                raise
                print "Error in photo saving:"
                return None

        return attachments

    def find_audio(self, req):
#        print "Audio", req
        op = self.api.audio.search
        args = {"q":req, "auto_complete" : 1, "search_own" : 0, "count" : 1}

        resp = rated_operation(op, args)
    
        try:
        #    print resp
            audio = resp["items"][0]
            self.update_stat("audio_found", 1)

            r = "audio"+str(audio["owner_id"])+"_"+str(audio["id"])
            print r
            return [r,]
        except:
            print "Error in audio find:"
            print pretty_dump(resp)
            return None

    def find_video(self, req):
 #       print "Find video",req
        op = self.api.video.search
        args = {"q":req, "adult":0, "search_own":0, "count":1}
        resp = rated_operation(op,args)
        try:
            video = resp["items"][0]
            self.update_stat("video_found", 1)
            r =  "video"+str(video["owner_id"])+"_"+str(video["id"])
            return [r,]
        except:
            print "Error in video find:"
            print pretty_dump(resp)
            return None

    def find_doc(self, req):
  #          print "Find doc",req
            op = self.api.docs.search
            args = {"q":req, "count":1}
            resp = rated_operation(op,args)
            try:   
                    doc = resp["items"][0]
                    self.update_stat("docs_found", 1)
                    r =  "doc"+str(doc["owner_id"])+"_"+str(doc["id"])
                    return [r,]
            except:
                    print "Error in video find:"
                    print pretty_dump(resp)
                    return None

    def find_wall(self, req):
   #         print "Find wall",req
            op = self.api.newsfeed.search
            args = {"q":req, "count":1}
            resp = rated_operation(op,args)
            try:
                    wall = resp["items"][0]
                    self.update_stat("walls_found", 1)
                    r =  "wall"+str(wall["owner_id"])+"_"+str(wall["id"])
                    return [r,]
            except:
                    print "Error in video find:"
                    print pretty_dump(resp)
                    return None

    def get_news(self, count=10):
            op = self.api.newsfeed.get
            args = {"filters":"post", "count":count}
            resp = rated_operation(op,args)
            return resp["items"]
    
    def like_post(self, post_id, owner_id):
            op = self.api.likes.add
            args = {"type":"post", "item_id":post_id, "owner_id":owner_id}
            resp = rated_operation(op,args)


    def friendStatus(self, user_ids):
        op = self.api.friends.areFriends
        args = {"user_ids":user_ids}
        resp = rated_operation(op,args)
        return resp

    def getUser(self,userid,fields,name_case):
        op = self.api.users.get
        args = {"user_ids":userid,"fields":fields,"name_case":name_case}
        resp = rated_operation(op,args)
        return resp[0]


    def friendAdd(self, user_id ):
        op = self.api.friends.add
        args = {"user_id":user_id}
        resp = rated_operation(op,args)
        return True

    def getRequests(self):
        op = self.api.friends.getRequests
        args = {}
        resp = rated_operation(op,args)
        print resp
        return resp["items"]

