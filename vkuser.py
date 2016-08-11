import json

import vk
import time
import json
import requests
from utils import *
import io
import sys
import traceback
from multiprocessing.pool import ThreadPool
import multiprocessing

class VkUser(object):

    def __init__(self, config, modconf, glb_update_stat):
        self.user = "tulen"
        self.modules = []
        self.modconf = modconf
        self.config = config
        self.glb_update_stat = glb_update_stat
        

        session = vk.Session(access_token=self.config["access"]["value"])
        
        self.api = vk.API(session,  v='5.50', timeout = 10)
        self.load_modules()
	self.thread_pool_modules = ThreadPool(4)
        self.thread_pool_msg = ThreadPool(4)
        self.mutex = multiprocessing.Lock()

    def load_modules(self):

        #load modules from self.config["enabled_moduled"]
        #load modules settings (for this user)
        self.modules = []
        for module in self.modconf["enabled_modules"]:
            package = __import__("modules"+"."+module)
            processor = getattr(package, module)
            modprocessor = processor.Processor(self.modconf["modules_settings"].get(module,{}), self)
            self.modules.append(modprocessor)
            print "Loaded module: [{}]".format("modules"+"."+module)
        self.prev_modules = self.modconf["enabled_modules"]
        self.prev_modules_settings = self.modconf["modules_settings"]

    def update_stat(self, stat, value):
        self.mutex.acquire()
        self.glb_update_stat(stat, value)
        self.mutex.release()

    def process_all_messages(self):
        operation = self.api.messages.get
        args = {"count" : self.config["message_count"]}
        ret = rated_operation( operation, args )
        messages  = ret["items"]
        self.process_messages(messages)

    def mark_messages(self, message_ids):
        operation = self.api.messages.markAsRead
        args = {"message_ids" : ",".join([str(x) for x in message_ids])}
        rated_operation( operation, args )

    def proc_msg_(self,message):
        
        if message["read_state"] != 0:
            return
    
        chatid = message.get("chat_id",None)
        userid = None

        if not chatid:
            userid = message.get("user_id", None)
        
        def thread_work(data):
            try:
                data[0].process_message(message=data[1], chatid=data[2], userid=data[3])
            except:
                print "Something wrong while processin user [{}]".format(self.user)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                self.update_stat("errors", 1)
            finally:
                self.update_stat("processed", 1)

        self.thread_pool_modules.map_async(thread_work, [(module, message, chatid, userid) for module in self.modules])

    def process_messages(self, messages):
        ids = [msg["id"] for msg in messages]
        self.mark_messages(ids)

        unread_messages = [ msg for msg in messages if msg["read_state"] == 0]
        if len(unread_messages) > 0:
            print "Maping ",len(unread_messages), "messages"
            self.thread_pool_msg.map_async(self.proc_msg_, unread_messages)

    def send_message(self, text="", chatid=None, userid=None, attachments=None):
        
        if not attachments:
            attachments = {}
            
        op = self.api.messages.send
        args = {"chat_id" :chatid, "user_id" : userid, "message" : text, "attachment" : attachments}

        print "sending message from [{}]".format(self.user)
        print pretty_dump(args)
        
        ret = rated_operation(op, args)
        
        if not ret:
            print "No answer for operation"

        self.update_stat("send", 1)

        if not ret:
            print "No answer for operation"

        
        
    def post(self, text, chatid, userid, attachments):

        oppost = self.api.wall.post
        args = {"owner_id" :int(self.config["access"]["user_id"]), "message" : text, "attachments" : ",".join(attachments)}
        print pretty_dump(args)
            
        print "Posting on wall".format(self.user)
        ret = rated_operation(oppost, args)
        print ret
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
        
        ids = self.__upload_images(upserver, files)
        
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveMessagesPhoto
                args = {"photo":i["photo"], "server":i["server"], "hash":i["hash"]}

                resp = rated_operation(op, args)
                #print resp
                attachments.append("photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:

                print "Error in photo saving:"
                return None

        self.update_stat("images_uploaded", len(attachments))
    
        return attachments

    def upload_images_files_wall(self, files):
        op = self.api.photos.getWallUploadServer
        args = {"group_id":int(self.config["access"]["user_id"])}
        upserver = rated_operation(op, args)

        photos = self.__upload_images(upserver,files)
        
        ids = photos
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveWallPhoto
                args = {"user_id":int(self.config["access"]["user_id"]),"group_id":int(self.config["access"]["user_id"]), "photo":i["photo"], "server":i["server"], "hash":i["hash"]}

                resp = rated_operation(op, args)
                #print resp
                attachments.append("photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:

                print "Error in photo saving:"
                return None

        return attachments


    def find_audio(self, req):
        print "Audio",req
        op = self.api.audio.search
        args = {"q":req, "auto_complete" : 1, "search_own" : 0, "count" : 1}

        resp = rated_operation(op, args)
        print resp
        try:
            audio = resp["items"][0]
            self.update_stat("audio_found", 1)

            r = "audio"+str(audio["owner_id"])+"_"+str(audio["id"])
            print "Returning ",r
            return [r,]
        except:
            print "Error in audio find:"
            print pretty_dump(resp)
            return None

    def find_video(self, req):
        op = self.api.video.search
        args = {"q":req, "adult":1, "search_own":0, "count":1}
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

