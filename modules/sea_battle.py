#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import yaml
import sea_battle_package as sbp

logger = logging.getLogger('tulen')

CONFIG_FILE = "conf.yaml"


def need_game_session(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        if game_manager.session_is_active():
            return f(*args)
        else:
            return

    return wrapper


def need_registration(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        if game_manager.is_team_registered():
            return f(*args)
        else:
            return sbp.NOT_REGISTERED_YET_MSG

    return wrapper


def need_valid_context(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.is_valid():
            return f(*args)
        else:
            return sbp.NO_MAP_YET_MSG

    return wrapper


def need_valid_map(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.is_valid():
            return f(*args)
        else:
            return sbp.NO_MAP_YET_MSG

    return wrapper


def need_opponent_set(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.opponent is None:
            return f(*args)
        else:
            return sbp.NO_OPPONENT_SET

    return wrapper


class Processor:
    def __init__(self, vkuser):
        self.config = yaml.load(open(vkuser.module_file("sea_battle", CONFIG_FILE)))
        self.user = vkuser
        self.game_manager = sbp.GameManager(vkuser)
        print self.config

    def is_answer_correct(self, answer, q_number):
        if answer == self.config["questions"][q_number].values()[0]:  # get the answer
            return True
        else:
            return False

    def start_game_session(self, msg):
        resp = self.game_manager.start_game_session()
        if resp:
            return resp

    @need_game_session
    def stop_game_session(self, msg):
        return self.game_manager.stop_game_session()

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

    @need_game_session
    def register(self, msg):
        # from forth word
        team_name = "".join(msg.split()[3:]).strip()
        return self.game_manager.register_team(team_name)

    # @sbp.need_valid_context
    @need_game_session
    @need_registration
    def questions(self, msg):
        return "\n".join([u"Вопрос {}: {}".format(i + 1, q.keys()[0]) for i, q in enumerate(self.config["questions"])])

    @need_game_session
    @need_registration
    # @need_valid_context       -- TODO: TMP!!!
    def answer(self, msg):
        # parse message as answer
        data = msg.split()[1:]

        if len(data) < 2:
            return sbp.INVALID_ANSWER_FORMAT_MSG
        try:
            q_number = int(data[0])
            q_answer = data[1].strip()
        except:
            return sbp.INVALID_ANSWER_FORMAT_MSG

        if q_number < 1 or q_number > len(self.config["questions"]):
            return sbp.INVALID_ANSWER_NUMBER_MSG

        return self.game_manager.question_answered(q_number - 1, self.is_answer_correct(q_answer, q_number - 1))

    # @sbp.need_valid_map
    @need_game_session
    @need_registration
    @need_valid_context
    def attack(self, msg):
        pass

    @need_game_session
    @need_registration
    @need_valid_context
    def game_request(self, msg):
        op_team_name = msg.split(sbp.gameRequest_command, 1)[1:][0].strip()
        answer = ""
        if self.game_manager.is_team_registered(op_team_name):
            answer += self.game_manager.start_game_with(op_team_name)
        else:
            return sbp.INVALID_OPPONENT_MSG

        # checking if current team (not op_team_name) is also awaited by op_team_name
        # if self.game_manager.opponent_available(team_name=op_team_name):
        #     return sbp.CAN_SHOT_MSG
        # else:
        #     return sbp.WAITING_FOR_OPPONENT_MSG

    @need_game_session
    @need_registration
    def load_map(self, msg):
        # from the third word
        field = "".join(msg.split()[2:]).strip()
        return self.game_manager.load_map(field)

    def process_message(self, message, chatid, userid):
        msg = message["body"].lower()

        user_id = userid
        if not user_id:
            user_id = message["user_id"]

        with self.game_manager(user_id, chatid):
            response_text = self.handler(msg)()
            if response_text:
                self.user.send_message(text=response_text, userid=userid, chatid=chatid)
