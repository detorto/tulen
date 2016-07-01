import json

import vk
import time
import json
import requests
from utils import *
import io
import sys
class VkUser(object):

	def __init__(self, config, modconf, glb_update_stat):
		self.user = "tulen"
		self.modules = []
		self.modconf = modconf
		self.config = config
		self.glb_update_stat = glb_update_stat
		
		self.load_modules()

		session = vk.Session(access_token=self.config["access"]["value"])
		
		self.api = vk.API(session,	v='5.50', timeout = 10)

	def load_context(self):

		self.context = load_json("./user_settings/{}.context".format(self.user))
		if not self.context:
			self.context = {"processed_messages":{}}

	def save_context(self):
		#save only message_count in processed_messages
		for id in self.context["processed_messages"]:

			if len(self.context["processed_messages"][id]) > self.config["message_count"]:

				self.context["processed_messages"][id] = self.context["processed_messages"][id][len(self.context["processed_messages"][id])-self.config["message_count"]: ]

		with io.open("./user_settings/{}.context".format(self.user), 'w', encoding='utf-8') as f:
			f.write(unicode(json.dumps(self.stats, ensure_ascii=False,indent=4, separators=(',', ': '))))

	def load_modules(self):

		#load modules from self.config["enabled_moduled"]
		#load modules settings (for this user)
		self.modules = []
		for module in self.modconf["enabled_modules"]:
			package = __import__("modules"+"."+module)
			processor = getattr(package, module)
			modprocessor = processor.Processor(self.modconf["modules_settings"][module], self)
			self.modules.append(modprocessor)
			print "Loaded module: [{}]".format("modules"+"."+module)
		self.prev_modules = self.modconf["enabled_modules"]
		self.prev_modules_settings = self.modconf["modules_settings"]

	def is_marked(self, message_id, chatid, userid):

		try:
			if  message_id in self.context["processed_messages"][str(chatid or userid)]:
				return True
			else:
				return False
		except:
				return False


	def update_stat(self, stat, value):
		self.glb_update_stat(stat, value)

	def process_all_messages(self):
		operation = self.api.messages.get
		args = {"count" : self.config["message_count"]}
		ret = rated_operation( operation, args )
		
		messages  = ret["items"]
		#print json.dumps(messages, sort_keys=True, indent=4, separators=(',', ': '))
		self.process_messages(messages)

	def mark_messages(self, message_ids):
		operation = self.api.messages.markAsRead
		args = {"message_ids" : ",".join([str(x) for x in message_ids])}
		rated_operation( operation, args )

	def process_messages(self, messages):
		ids = []
		for message in messages:
			
			if message["read_state"] != 0:
				continue

			ids.append(message["id"])
			

			chatid = None
			userid = None
			
			if "chat_id" in message:
				chatid = message["chat_id"]
			else:
				userid = message["user_id"]

			try:
				for module in self.modules:
					module.process_message(message, chatid=chatid, userid=userid)
				#self.mark_messages(ids)
			except:
				import traceback
				print "Something wrong while processin user [{}]".format(self.user)
		                exc_type, exc_value, exc_traceback = sys.exc_info()
                		traceback.print_exception(exc_type, exc_value, exc_traceback)

			finally:
				self.update_stat("processed", 1)
		if ids:
			self.mark_messages(ids)


	def send_message(self, text="" , chatid=None, userid=None, attachments=None):
		if not attachments:
			attachments = {}
			
		op = self.api.messages.send
		args = {"chat_id" :chatid, "user_id" : userid, "message" : text, "attachment" : attachments.get("message",None)}

		print "sending message from [{}]".format(self.user)
		print pretty_dump(args)
		
		ret = rated_operation(op, args)
		
		if not ret:
			print "No answer for operation"

		self.update_stat("send", 1)

		
		if attachments:
			self.update_stat("attachments", len(attachments))

			oppost = self.api.wall.post
			args = {"owner_id" :int(self.config["access"]["user_id"]), "message" : text, "attachments" : ",".join(attachments.get("wall",None))}
			print pretty_dump(args)
		
			print "Posting on wall".format(self.user)
			ret = rated_operation(oppost, args)
			print ret
		
		if not ret:
			print "No answer for operation"

		self.update_stat("post", 1)
		

	def upload_images_files(self, files):
		op = self.api.photos.getMessagesUploadServer
		args = {}
		upserver = rated_operation(op, args)
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
				print "Error in photo uploading:"
			


		ids = photos
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
		attachments  = {"message":attachments, "wall": self.upload_images_files_wall(files)}
		return attachments

	def upload_images_files_wall(self, files):
		op = self.api.photos.getWallUploadServer
		args = {"group_id":int(self.config["access"]["user_id"])}
		upserver = rated_operation(op, args)
		print upserver

		photos = []
		for f in files:
			op = requests.post
			args = {"url" : upserver["upload_url"], "files" : {'photo': (f.split("/")[-1], open(f, 'rb'))}}
			try:
				response = op(**args)
				pj =  response.json()
				print pj
				ph = {"photo":pj["photo"], "server":pj["server"],"hash":pj["hash"]}
				photos.append(ph)
			except:
				print "Error in photo uploading:"
				


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

		#self.update_stat("images_uploaded", len(attachments))
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
			return {"wall":[r],"message":[r]}
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
			return {"wall":[r], "message":[r]}
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
                        return {"wall":[r], "message":[r]}
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
                        return {"wall":[r], "message":[r]}
                except:
                        print "Error in video find:"
                        print pretty_dump(resp)
                        return None


