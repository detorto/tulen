#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import io
import yaml
from datetime import datetime, timedelta
import random
from threading import Timer
import logging

from utils import enum

logger = logging.getLogger('tulen')

CONFIG_FILE = "conf.yaml"

# TODO: can this be different??
MAP_SIZE = 10



Orientation = enum('Horizontal', 'Vertical')
# Orientation.reverse_mapping['Horizontal']

MAP_EXAMPLE =   """
                0 0 0 1 0 0 3 0 0 1
                2 2 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 4 4 4 4 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 5 5 5 5 5 0
                0 0 0 0 0 0 0 0 0 0
                """

# simple game commands
loadMap_command = u"загрузи карту "

game_commands = [loadMap_command]

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ship:
    def __int__(self, ship_size, begin, end):
        self.ship_size = ship_size
        self.begin = begin
        self.end = end
        try:
            if begin.x != end.x:
                self.orientation = Orientation.Horizontal
            elif begin.y != end.y:
                self.orientation = Orientation.Vertical
            else:
                print "Error???"
        except Exception as e:
            print e.message


    def try_hit(self, coordiante):
        pass

class Player:
    def __init__(self, player_id):
        self.player_id = player_id

class Map:
    def __init__(self, map_data, user_id):
        self.user_id = user_id
        self.map_data = map_data

    @classmethod
    def parse_data(cls, map_data, user_id):
        try:
            map_data = [[map_data[i][j] for i in range(MAP_SIZE)] for j in range(MAP_SIZE)]
        except Exception as e:
            logger.error(
                "SeaBattle module (user_id:{}): Exception occurred while setting alarm clock message - {}"
                    .format(user_id, e.message))
    @classmethod
    def from_file(cls, file_path, user_id):
        try:
            with io.open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    print line
        except Exception as e:
            print e


class Processor:
    def __init__(self, vkuser):
        self.alarms = {}
        self.config = yaml.load(open(vkuser.module_file("alarm", CONFIG_FILE)))
        self.user = vkuser
        self.game_started = False

    def process_message(self, message, chatid, userid):
        pass