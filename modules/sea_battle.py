#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import yaml
import sea_battle_package as sbp

logger = logging.getLogger('tulen')

CONFIG_FILE = "conf.yaml"


class Processor:
    def __init__(self, vkuser):
        self.config = yaml.load(open(vkuser.module_file("sea_battle", CONFIG_FILE)))
        self.user = vkuser
        self.game_manager = sbp.GameManager(vkuser, self.config["questions"])
        print self.config

    def start_game_session(self, msg):
        return self.game_manager.start_game_session(msg)

    def register(self, msg):
        return self.game_manager.register_team(msg)

    def questions(self, msg):
        return self.game_manager.get_questions(msg)

    def load_map(self, msg):
        return self.game_manager.load_map(msg)

    def game_request(self, msg):
        return self.game_manager.game_request(msg)

    def answer(self, msg):
        return self.game_manager.parse_answer(msg)

    def attack(self, msg):
        return self.game_manager.attack(msg)

    def stop_game_session(self, msg):
        return self.game_manager.stop_game_session(msg)

    def handler(self, message):
        # dummy answer (if nothing fit or session ain't started)
        def dummy():
            def call():
                return ""

        # map of request_text - handlers
        mapper = {sbp.start_game_processing_command: self.start_game_session,
                  sbp.stop_game_processing_command: self.stop_game_session,
                  sbp.answer_command: self.answer,
                  sbp.gameRequest_command: self.game_request,
                  sbp.attack_command: self.attack,
                  sbp.questions_command: self.questions,
                  sbp.loadMap_command: self.load_map,
                  sbp.registerTeam_command: self.register}

        # wrapper for method with param
        def wrapper(funk, msg):
            def call():
                return funk(msg)

            return call

        # return necessary method
        for k, v in mapper.items():
            if k in message:
                return wrapper(v, message)

        return dummy

    def process_message(self, message, chatid, userid):
        msg = message["body"].lower()

        user_id = userid
        if not user_id:
            user_id = message["user_id"]

        with self.game_manager(user_id, chatid):
            response_text = self.handler(msg)()
            if response_text:
                self.user.send_message(text=response_text, userid=userid, chatid=chatid)
