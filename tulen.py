#!/usr/bin/python
# -*- coding: utf-8 -*-


#import vk

import urllib2
import requests

import pkgutil
import imp
import os

import threading
import json
import time

from vkuser import VkUser
from utils import *
import sys
import traceback
import io

#url for getting access_token
#https://oauth.vk.com/authorize?client_id=4775188&display=page&redirect_uri=http://oauth.vk.com/blank&scope=audio,offline,friends,messages,photos,video&response_type=token&v=5.37


def process(config):
	
	def update_stat(stat, value):
		statistics = config.get("statistics",{})

		upd = statistics.get(stat, 0)
		upd += value;	
		config["statistics"][stat] = upd

		with io.open("config.json", 'w', encoding='utf-8') as f:
			f.write(unicode(json.dumps(config, ensure_ascii=False,indent=4, separators=(',', ': '))))

	while True: 
		try:
			print "Loading modules configuration... "
			modules = load_json("modules.json");
		except:
			print "Invalid modules config !"
			time.sleep(10)
			continue

		try:
			print "Creating user api... "
			vkuser = VkUser(config, modules, update_stat)
			break
		except:
			print "Bad thing happenes on userapi creation !"
			
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)

			time.sleep(10)
		

	print "Starting processing... "
	while True:
		try:
			vkuser.process_all_messages()
		except:
			print "Something wrong while processin dialogs [{}]"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)


def main():
	print "*************Tulen vk.com bot****************"

	config = load_json("config.json");

	print "Loaded configuration"
	
	print pretty_dump(config)

	if not config:
		print "Invalid config.json file!"
		exit(0)

	process(config)
	
if __name__ == '__main__':
	main()

