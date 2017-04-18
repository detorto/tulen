# coding: utf-8
import time
import json
import requests
import io
import sys
import os
import logging
import random
import threading
from multiprocessing.pool import ThreadPool
import multiprocessing

import vk
import utils
import vkrequest

sys.path.append("./modules")
logger = logging.getLogger('tulen')
logger.setLevel(logging.DEBUG)

vk_script_getmsg = """var k = 200;
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


class VkUser(object):
    #return the file form config directory for module name
    #used by modules
    def module_file(self,  modname, filename):
        return os.path.join(self.config.get("modules_config_dir", "config"),modname, filename)
    
    def init_globals(self):
        # for proper random
        random.seed(time.time())

        # captcha init: if no captcha section in config, pass it
        captcha_config = self.config.get("anticaptcha", None)
        if not captcha_config:
            logger.warning("Anticaptcha cant be intialized: no config")

        else:

            service = captcha_config["service"]
            creds = captcha_config["credentials"]
            vkrequest.init_captcha(service, creds)
            logger.info("Captcha [{}] initialized. balance: {}".format(service,
                                                                       vkrequest.captcha.balance()))

        # enable ratelimiting
        vkrequest.run_ratelimit_dispatcher()

        logger.info("Rate-limit dispatcher started")

        logger.info("Global systems initialized")

    def init_vk_session(self):
        if self.testmode:
            self.api = None
            logger.info("VK Session: test mode")
        else:
            session = vk.Session(access_token=self.config["access_token"]["value"])

            timeout = self.config["access_token"].get("connection_timeout", 10)
            self.my_uid = self.config["access_token"]["user_id"]
            if not self.my_uid:
                raise RuntimeError("Access config: user_id not defined")

            self.api = vk.API(session,  v='5.50', timeout=timeout)

            logger.info("VK Session: real mode [{}]".format(self.my_uid))

    def init_modules(self):
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
        logger.info("All modules loaded.")

    def load_modules(self, mod_list):
        self.modules = {"global":[], "unique":[], "parallel": []}

        def add_module(modif, modproc):
            modules = self.modules.get(modif, [])
            modules.append(modproc)
            self.modules[modif] = modules

        for module in mod_list:
            data = module.split()
            modif = "parallel"
            module = data[0]
            if len(data) > 1:
                modif = data[0]
                module = data[1]

            package = __import__("modules"+"."+module)
            processor = getattr(package, module)
            modprocessor = processor.Processor(self)

            add_module(modif, modprocessor)

            logger.info("Loaded module: [{}] as {}".format(
                "modules"+"."+module, modif))

    def init_multithreading(self):
        self.msg_queue = {}

        # create message queue: general (first step for uniq modules)
        self.msg_queue["general"] = multiprocessing.Queue()
        # create message queues: paralel (for parallel message processing)
        self.msg_queue["parallel"] = multiprocessing.Queue()

        self.msg_processors = {}

        # create threads for general messages, and for parallel mesages
        # they will pick-up messages from queues
        msg_thread_count = int(self.config.get("msg_threads", 4))
        mod_thread_count = int(self.config.get("mod_threads", 4))

        self.msg_processors["general"] = [threading.Thread(target=self.process_message_general)
                                          for x in range(msg_thread_count)]
        self.msg_processors["parallel"] = [threading.Thread(target=self.process_message_parallel)
                                           for x in range(mod_thread_count)]
        # lauch this threads
        [t.start() for t in self.msg_processors["general"]]
        [t.start() for t in self.msg_processors["parallel"]]

        logger.info("Multithreading intialized: {}x{} grid.".format(
            msg_thread_count, mod_thread_count))

    def __init__(self, config, testmode=False, onlyforuid=None):
        self.config = config
        if onlyforuid:
            onlyforuid = int(onlyforuid)
        self.onlyforuid = onlyforuid
        self.testmode = testmode

        self.init_globals()
        self.init_vk_session()
        self.init_modules()

        self.init_multithreading()
        logger.info("All intializing complete")

    def poll_messages(self):
        if self.testmode:
            msg = raw_input("msg>> ")
            messages = [
                {"read_state": 0, "id": "0", "body": msg, "chat_id": 2}]
        else:
            operation = self.api.execute
            args = {"code": vk_script_getmsg}
            ret = vkrequest.perform(operation, args)
            messages = ret["items"]

        return messages

    def process_messages(self, messages):
        unread_messages = [msg for msg in messages if msg["read_state"] == 0]

        # filter messages if they are for specified uid
        if self.onlyforuid:
            unread_messages = [msg for msg in unread_messages if msg[
                "user_id"] == self.onlyforuid]

        if len(unread_messages) > 0:
            logger.info("Unread messages: {}".format(len(unread_messages)))

            # global modes cant stop the message, i think
            for m in unread_messages:
                self.process_message_global(m)

            logger.debug("Sending messages to general queue [{}]".format(len(unread_messages)))

            [self.msg_queue["general"].put(message) for message in unread_messages]

    def process_message_global(self, message):
        try:
            for mod in self.modules["global"]:
                self.process_message_in_module(mod, message)
        except:
            logger.exception("Error in global modules processing")

    def process_message_in_module(self, module, message):

        # because VK want only user_id or chat_id, and chat_id in priority
        chatid = message.get("chat_id", None)
        userid = None

        if not chatid:
            userid = message.get("user_id", None)

        return module.process_message(message, chatid, userid)
    # general processing thread: picks messages from general queue

    def process_message_general(self):

        def process_in_unique_modules(message):
            for m in self.modules["unique"]:
                if self.process_message_in_module(m, message) == True:
                    logger.info("Unique module {} worked".format(m.__class__))
                    return True
            return False

        while True:
            try:
                message = self.msg_queue["general"].get()

                # if one of the uniq modules returned true, do not process
                # message next
                if process_in_unique_modules(message):
                    # pick new message
                    continue

                logger.info("Sending message to parallel modules")
                # multiply message in count of parallel module.
                # processor will take it and use corresponding module
                # cant pass in it the module itself, because thread obj cant be
                # pickled
                for i, _ in enumerate(self.modules["parallel"]):
                    self.msg_queue["parallel"].put((message, i))
            except:
                logger.exception("Processing in general failed")

    def process_message_parallel(self):
        while True:
            try:
                message, module_index = self.msg_queue["parallel"].get()
                logger.debug("Parallel message processing in {}"
                             .format(self.modules["parallel"][module_index].__class__))

                self.process_message_in_module(
                    self.modules["parallel"][module_index], message)
            except:
                logger.exception("Processing in parallel failed")

    # shorcuts for common-use vk-api requests
    def send_message(self, text="", chatid=None, userid=None, attachments=None):
        if self.testmode:
            print("----", text, attachments)
            return

        if not attachments:
            attachments = {}

        op = self.api.messages.send

        # change some cirillic to latin
        # for not to triger another tulen
        text = text.replace(u"а", u"a")
        text = text.replace(u"е", u"e")
        text = text.replace(u"о", u"o")
        text = text.replace(u"с", u"c")

        # to send message for username, not userid
        args = {"chat_id": chatid, "message": text, "attachment": attachments,
                "random_id": random.randint(0xfff, 0xffffff)}

        if isinstance(userid, int):
            args.update({"user_id": userid})
        else:
            args.update({"domain": userid})

        ret = vkrequest.perform(op, args)

        if not ret:
            logger.warning("No answer for send message request")

        logger.info("Sent message to c[{}]:u[{}] with attachment [{}]".format(chatid,
                                                                              userid,
                                                                              repr(attachments)))

        logger.info("response is {}".format(repr(ret)))
        return ret

    def get_all_friends(self, fields):
        operation = self.api.friends.get
        args = {"fields": fields}
        ret = vkrequest.perform(operation, args)
        logger.info("Got friends")
        return ret

    def send_sticker(self, user_id, peer_id, chat_id, sticker_id=0):
        op = self.api.messages.sendSticker

        args = {"peer_id": peer_id, "chat_id": chat_id,
                "random_id": random.randint(0xfff, 0xffffff),
                "sticker_id": random.randint(1, 168) if sticker_id == 0 else sticker_id}

        if isinstance(user_id, int):
            args.update({"user_id": user_id})
        else:
            args.update({"domain": user_id})

        ret = vkrequest.perform(op, args)

        # wtf???
        if ret == 100 or (900 <= ret <= 902):
            logger.warning("Sent sticker response is {}".format(repr(ret)))
            args["random_id"] = random.randint(0xfff, 0xffffff)
            args["sticker_id"] = random.randint(1, 168)
            ret = vkrequest.perform(op, args)

        logger.info("Sent sticker")
        return ret

    def post(self, text, chatid, userid, attachments):

        oppost = self.api.wall.post
        args = {"owner_id": self.my_uid, "message": text,
                "attachments": ",".join(attachments)}

        ret = rated_operation(oppost, args)
        log.info("Wall post created")

        return ret

    def __upload_images_vk(self, upserver, files):
        photos = []
        for f in files:
            op = requests.post
            filename = f.split("/")[-1]
            args = {"url": upserver["upload_url"], "files": {'photo': (filename, open(f, 'rb'))}}
            try:
                # i think we do not need to use rate-limit operation here
                response = vkrequest.perform_now(op, args)
                ph = {"photo": response["photo"], 
                      "server": response["server"], 
                      "hash": response["hash"]}
                photos.append(ph)
            except:
                logger.exception("Upload images failed")

        return photos

    def upload_images_files(self, files):
        logger.info("Uploading message images...")
        op = self.api.photos.getMessagesUploadServer
        args = {}

        upserver = vkrequest.perform(op, args)
        ids = self.__upload_images_vk(upserver, files)
        logger.info("Uploaded message images")
        attachments = []

        for i in ids:
            try:
                op = self.api.photos.saveMessagesPhoto
                args = {"photo": i["photo"], "server": i[
                    "server"], "hash": i["hash"]}

                resp = vkrequest.perform(op, args)
                attachments.append(
                    "photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:
                logger.exception("Saving message image failed")
                return None

        return attachments

    def upload_images_files_wall(self, files):

        logger.info("Uploading wall images...")
        op = self.api.photos.getWallUploadServer
        args = {"group_id": self.my_uid}

        upserver = vkrequest.perform(op, args)
        photos = self.__upload_images(upserver, files)
        logger.info("Uploaded wall images")
        ids = photos
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveWallPhoto
                args = {"user_id": self.my_uid,
                        "group_id": self.my_uid,
                        "photo": i["photo"],
                        "server": i["server"],
                        "hash": i["hash"]}

                resp = vkrequest.perform(op, args)
                attachments.append(
                    "photo"+str(resp[0]["owner_id"])+"_"+str(resp[0]["id"]))
            except:
                logger.exception("Saving wall image failed")
                raise

        return attachments

    def find_video(self, req):
        log.info("Looking for requested video")
        op = self.api.video.search
        args = {"q": req, "adult": 0, "search_own": 0, "count": 1}
        resp = vkrequest.perform(op, args)
        try:
            video = resp["items"][0]
            r = "video"+str(video["owner_id"])+"_"+str(video["id"])
            return [r, ]
        except:
            logger.exception("Video search failed")
            return None

    def find_doc(self, req):
        log.info("Looking for document")
        op = self.api.docs.search
        args = {"q": req, "count": 1}
        resp = vkrequest.perform(op, args)
        try:
            doc = resp["items"][0]
            r = "doc"+str(doc["owner_id"])+"_"+str(doc["id"])
            return [r, ]
        except:
            logger.exception("Document logging failed")
            return None

    def find_wall(self, req):
        log.info("Looking for wall post")
        op = self.api.newsfeed.search
        args = {"q": req, "count": 1}
        resp = vkrequest.perform(op, args)
        try:
            wall = resp["items"][0]
            r = "wall"+str(wall["owner_id"])+"_"+str(wall["id"])
            return [r, ]
        except:
            logger.exception("Wall post search failed")
            return None

    def get_news(self, count=10):
        logger.info("Gathering newsfeed")
        op = self.api.newsfeed.get
        args = {"filters": "post", "count": count}
        resp = vkrequest.perform(op, args)
        return resp["items"]

    def like_post(self, post_id, owner_id):
        logger.info("Liking post")
        op = self.api.likes.add
        args = {"type": "post", "item_id": post_id, "owner_id": owner_id}
        resp = vkrequest.perform(op, args)

    def friendStatus(self, user_ids):
        logger.info("Getting friend status")
        op = self.api.friends.areFriends
        args = {"user_ids": user_ids}
        resp = vkrequest.perform(op, args)
        return resp

    def getUser(self, userid, fields, name_case):
        logger.info("Getting user information")
        op = self.api.users.get
        args = {"user_ids": userid, "fields": fields, "name_case": name_case}
        resp = vkrequest.perform(op, args)
        return resp[0]

    def friendAdd(self, user_id):
        logger.info("Adding to friends")
        op = self.api.friends.add
        args = {"user_id": user_id}
        resp = vkrequest.perform(op, args)
        return True

    def getRequests(self):
        logger.info("Getting  friends requests")
        op = self.api.friends.getRequests
        args = {}
        resp = vkrequest.perform(op, args)
        return resp["items"]