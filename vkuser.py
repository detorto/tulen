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
import os
import logging
import random

logger = logging.getLogger('tulen')


class VkUser(object):
    def __init__(self, config, update_stat, testmode=False, test_scenario=None):
        self.config = config
        self.test_scenario = test_scenario

        self.update_stat_ = update_stat

        if testmode:
            session = None
            self.api = None
            logger.info("Running in test mode")
        else:
            session = vk.Session(access_token=self.config["access_token"]["value"])
            self.api = vk.API(session, v='5.60', timeout=10)
            logger.info("VK API created")

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
        self.thread_pool_msg = ThreadPool(int(config.get("msg_threads", 4)))
        self.mutex = multiprocessing.Lock()
        logger.info("Multiprocessing intiated: " + str(self.thread_pool_modules) + " " + str(self.thread_pool_modules))
        self.testmode = testmode

    def load_modules(self, mod_list):

        self.modules = []

        for module in mod_list:
            package = __import__("modules" + "." + module)
            processor = getattr(package, module)
            modprocessor = processor.Processor(self)
            self.modules.append(modprocessor)
            self.exclusive_modules = [m for m in self.modules if getattr(m, "exclusive", False) == True]
            self.parallel_modules = [m for m in self.modules if not getattr(m, "exclusive", False) == True]

            logger.info("Loaded module: [{}]".format("modules" + "." + module))

    def module_file(self, modname, filename):
        return os.path.join(self.config.get("modules_config_dir", "config"), modname, filename)

    def update_stat(self, stat, value):
        logger.debug("Mutex acuire")
        self.mutex.acquire()
        logger.debug("Mutex acuired")
        self.update_stat_(stat, value)
        self.mutex.release()
        logger.debug("Mutex released")

    def process_test_scenarios(self):
        try:
            messages = []
            if self.test_scenario is not None and self.test_scenario["enabled"] and not self.test_scenario["processed"]:
                self.test_scenario["processed"] = True
                users = self.test_scenario["users"]
                if len(users) > 0:
                    processing = True
                    i = 0
                    while processing:
                        processing = False
                        for user_name in users:
                            user = self.test_scenario[user_name]
                            if i < len(user["messages"]):
                                messages.append({"read_state": 0,
                                                 "id": user["uid"],
                                                 "user_id": user["uid"],
                                                 "chat_id": user["chat_id"],
                                                 "body": user["messages"][i]})
                                processing = True
                        i += 1
            return messages
        except Exception as e:
            logger.debug("Exception occurred while processing test scenarios: {}".format(e.message))
            return []

    def process_all_messages(self):
        logger.debug("Retrieving messages")
        if self.testmode:
            messages = self.process_test_scenarios()
            if len(messages) == 0:
                msg = raw_input("msg>> ")
                msg = msg.decode('utf-8')
                messages = [{"read_state": 0, "id": "0", "body": msg, "chat_id": 2}]
        else:
            operation = self.api.messages.get
            args = {"count": self.config["message_count"]}
            ret = rated_operation(operation, args)
            messages = ret["items"]

        self.process_messages(messages)

    def get_all_friends(self, fields):
        logger.debug("Retrieving messages")

        operation = self.api.friends.get
        args = {"fields": fields}
        return rated_operation(operation, args)

    def mark_messages(self, message_ids):
        logger.debug("Marking messages: {}".format(",".join([str(a) for a in message_ids])))
        if self.testmode:
            return

        operation = self.api.messages.markAsRead
        args = {"message_ids": ",".join([str(x) for x in message_ids])}
        rated_operation(operation, args)

    def proc_msg_(self, message):
        logger.debug("Processing msg {}".format(str(message)))

        chatid = message.get("chat_id", None)
        userid = None

        if not chatid:
            userid = message.get("user_id", None)

        def thread_work(data):
            try:
                return data[0].process_message(message=data[1], chatid=data[2], userid=data[3])
            except:
                logger.error("Something wrong while processin {}".format(str(data)))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                self.update_stat("errors", 1)

        logger.debug("Mapping message between modules")
        print "Exmods:", len(self.exclusive_modules)
        for m in self.exclusive_modules:

            if thread_work((m, message, chatid, userid)) == True:
                print "Excl module", m.__class__, "worked"
                return

        self.thread_pool_modules.map_async(thread_work,
                                           [(module, message, chatid, userid) for module in self.parallel_modules])

    def process_messages(self, messages):
        ids = [msg["id"] for msg in messages]
        self.mark_messages(ids)

        unread_messages = [msg for msg in messages if msg["read_state"] == 0]
        if len(unread_messages) > 0:
            logger.info("Unread messages: {}".format("\n".join([m["body"].encode("utf8") for m in unread_messages])))

        if len(unread_messages) > 0:
            logger.debug("Mapping message between msg processors [{}]".format(len(unread_messages)))
            self.thread_pool_msg.map_async(self.proc_msg_, unread_messages)
            self.update_stat("processes", len(unread_messages))

    def send_message(self, text="", chatid=None, userid=None, attachments=None):
        try:
            logger.info("Sending msg [{}] to c[{}]:u[{}] with attachment [{}]".format(text,
                                                                                      chatid,
                                                                                      userid,
                                                                                      repr(attachments)))
        except:
            logger.info("Sending some unformated !!!!! msg to {}:{}".format(chatid, userid))
        if self.testmode:
            print "----", text, attachments
            return

        if not attachments:
            attachments = {}

        op = self.api.messages.send
        if isinstance(userid, (int, long)):
            args = {"chat_id": chatid, "user_id": userid, "message": text, "attachment": attachments}
        else:
            args = {"chat_id": chatid, "domain": userid, "message": text, "attachment": attachments}
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
        # return None
        oppost = self.api.wall.post
        args = {"owner_id": int(self.config["access_token"]["user_id"]), "message": text,
                "attachments": ",".join(attachments)}

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
            args = {"url": upserver["upload_url"], "files": {'photo': (f.split("/")[-1], open(f, 'rb'))}}
            try:
                response = op(**args)
                pj = response.json()
                ph = {"photo": pj["photo"], "server": pj["server"], "hash": pj["hash"]}
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
                args = {"photo": i["photo"], "server": i["server"], "hash": i["hash"]}

                resp = rated_operation(op, args)
                print "Uload resp:", resp
                attachments.append("photo" + str(resp[0]["owner_id"]) + "_" + str(resp[0]["id"]))
            except:

                print "Error in photo saving:"
                return None

        self.update_stat("images_uploaded", len(attachments))

        return attachments

    def upload_images_files_wall(self, files):
        # return []
        op = self.api.photos.getWallUploadServer
        args = {"group_id": int(self.config["access_token"]["user_id"])}
        upserver = rated_operation(op, args)

        photos = self.__upload_images(upserver, files)

        ids = photos
        attachments = []
        for i in ids:
            try:
                op = self.api.photos.saveWallPhoto
                args = {"user_id": int(self.config["access_token"]["user_id"]),
                        "group_id": int(self.config["access_token"]["user_id"]), "photo": i["photo"],
                        "server": i["server"], "hash": i["hash"]}

                resp = rated_operation(op, args)

                attachments.append("photo" + str(resp[0]["owner_id"]) + "_" + str(resp[0]["id"]))
            except:
                raise
                print "Error in photo saving:"
                return None

        return attachments

    def find_audio(self, req):
        print "Audio", req
        op = self.api.audio.search
        args = {"q": req, "auto_complete": 1, "search_own": 0, "count": 1}

        resp = rated_operation(op, args)

        try:
            audio = resp["items"][0]
            self.update_stat("audio_found", 1)

            r = "audio" + str(audio["owner_id"]) + "_" + str(audio["id"])
            return [r, ]
        except:
            print "Error in audio find:"
            print pretty_dump(resp)
            return None

    def find_video(self, req):
        print "Find video", req
        op = self.api.video.search
        args = {"q": req, "adult": 1, "search_own": 0, "count": 1}
        resp = rated_operation(op, args)
        try:
            video = resp["items"][0]
            self.update_stat("video_found", 1)
            r = "video" + str(video["owner_id"]) + "_" + str(video["id"])
            return [r, ]
        except:
            print "Error in video find:"
            print pretty_dump(resp)
            return None

    def find_doc(self, req):
        print "Find doc", req
        op = self.api.docs.search
        args = {"q": req, "count": 1}
        resp = rated_operation(op, args)
        try:
            doc = resp["items"][0]
            self.update_stat("docs_found", 1)
            r = "doc" + str(doc["owner_id"]) + "_" + str(doc["id"])
            return [r, ]
        except:
            print "Error in video find:"
            print pretty_dump(resp)
            return None

    def find_wall(self, req):
        print "Find wall", req
        op = self.api.newsfeed.search
        args = {"q": req, "count": 1}
        resp = rated_operation(op, args)
        try:
            wall = resp["items"][0]
            self.update_stat("walls_found", 1)
            r = "wall" + str(wall["owner_id"]) + "_" + str(wall["id"])
            return [r, ]
        except:
            print "Error in video find:"
            print pretty_dump(resp)
            return None

    def get_news(self, count=10):
        op = self.api.newsfeed.get
        args = {"filters": "post", "count": count}
        resp = rated_operation(op, args)
        return resp["items"]

    def like_post(self, post_id, owner_id):
        op = self.api.likes.add
        args = {"type": "post", "item_id": post_id, "owner_id": owner_id}
        resp = rated_operation(op, args)

    def friendStatus(self, user_id):
        op = self.api.friends.areFriends
        args = {"user_ids": user_id}
        resp = rated_operation(op, args)
        return resp[0]["friend_status"]

    def getUser(self, userid, fields, name_case):
        op = self.api.users.get
        args = {"user_ids": userid, "fields": fields, "name_case": name_case}
        resp = rated_operation(op, args)
        return resp[0]

    def friendAdd(self, user_id):
        op = self.api.friends.add
        args = {"user_id": user_id}
        resp = rated_operation(op, args)
        return True
