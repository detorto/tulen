#!/usr/bin/python
# -*- coding: utf-8 -*-

from game_context import *
from ship_processing import Point as _Point
from datetime import datetime
import threading
import os


class GameManager:
    def __init__(self, vk_user, questions):
        self.lock = threading.Lock()
        self.vk_user = vk_user
        self.questions = questions
        self.max_score = 10

        self.teams = {}
        self.games = []
        self.active_sessions = []

        self.load()

    def __call__(self, uid, chat_id):
        self.uid = uid
        self.chat_id = chat_id
        self.load()
        team_name = self.get_team_name()
        self.game_context = GameContext(uid, self.max_score, team_name, self.get_opponent_name(team_name))

        if self.check_winner():
            self.stop_game_session()

        return self

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
        if self.check_winner():
            self.stop_game_session()
        else:
            self.save()
            self.game_context.save()
        self.lock.release()

    #   game commands   ================================================================================================

    @need_no_game_session
    def start_game_session(self, message=""):
        self.active_sessions.append({"session_uid": self.uid,
                                     "session_started": datetime.now().strftime("%d.%m.%Y %H:%M:%S")})
        return SESSION_STARTED_MSG.format(self.uid)

    @need_game_session
    @need_game_not_started
    @can_register_team
    def register_team(self, message):
        # from forth word
        team_name = "".join(message.split()[3:]).strip()

        self.teams[team_name] = {"team_uid": self.uid, "team_chat_id": self.chat_id}
        self.game_context.this_team_name = team_name
        self.game_context.this_team = self.game_context.create_team(team_name, self.uid)

        return REGISTERED_TEAM_MSG.format(team_name, self.uid)

    @need_game_session
    @need_registration
    def get_questions(self, message=""):
        return "\n".join([u"Вопрос {}: {}".format(i + 1, q.keys()[0]) for i, q in enumerate(self.questions)])

    @need_game_session
    @need_registration
    @need_game_not_started
    def load_map(self, message):
        # from the third word
        field = "".join(message.split()[2:]).strip()
        self.game_context.this_team.field = field
        return self.game_context.this_team.parse_fields()

    @need_game_session
    @need_registration
    @need_game_not_started
    @need_valid_map
    @need_no_opponent_set
    def game_request(self, message):
        try:
            op_team_name = message.split(gameRequest_command, 1)[1:][0].strip()

            if not op_team_name or op_team_name not in self.teams:
                return UNKNOWN_TEAM_MSG.format(op_team_name)

            return self.start_game_with(op_team_name)
        except Exception as e:
            print "Exception occurred while parsing opponent team name"

    @need_game_session
    @need_registration
    @need_valid_map
    @need_opponent_set
    @need_game_started
    def parse_answer(self, message):
        data = message.split()[1:]
        if len(data) < 2:
            return message.INVALID_ANSWER_FORMAT_MSG
        try:
            q_number = int(data[0])
            q_answer = data[1].strip()
        except:
            return INVALID_ANSWER_FORMAT_MSG

        if q_number < 1 or q_number > len(self.questions):
            return INVALID_ANSWER_NUMBER_MSG

        return self.question_answered(q_number - 1, self.is_answer_correct(q_answer, q_number - 1))

    @need_game_session
    @need_registration
    @need_valid_map
    @need_opponent_set
    @need_game_started
    def attack(self, message):
        coords_str = message[message.index(attack_command) + len(attack_command):]
        hit_point = _Point.try_parse(coords_str)
        if hit_point:
            for ship in self.game_context.this_team.ships:
                ret_val = ship.try_attack(hit_point)
                if ret_val:
                    return ret_val
            return u"Сорян, мимо"
        return u"Ты втираешь мне какую-то дичь! (вы ошиблись с форматом координат)"

    @staticmethod
    def save_game_results(file_name, data):
        try:
            with open(file_name, 'w') as outfile:
                data = {"winner": data["winner"],
                        "looser": data["looser"],
                        "winner_score": data["winner_score"],
                        "looser_score": data["looser_score"],
                        "game_started": data["game_started"],
                        "game_finished": data["game_finished"]}
                yaml.dump(data, outfile, default_flow_style=True)
        except Exception as e:
            print "Exception occured while saving game results for (winner {}, looser {}) - {}" \
                .format(data["winner"], data["looser"], e.message)

    @need_game_session
    def stop_game_session(self, message=""):
        self.active_sessions = [session for session in self.active_sessions if session["session_uid"] != self.uid]

        # Check the winner, save game data, send message about game ending to both players,
        # delete both teams from self.teams, and current game from self.games

        team_name = self.get_team_name()
        opponent_name = self.get_opponent_name()

        if team_name:
            game, i = self.get_game_data(team_name=team_name)
            if game and self.game_context.is_game_started():
                gc = self.game_context
                winner_name = self.check_winner()
                if not winner_name:
                    winner_name = opponent_name

                winner = gc.this_team if gc.this_team_name == winner_name else gc.opponent
                looser = gc.this_team if gc.this_team_name != winner_name else gc.opponent

                game_finished = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                data = {"winner": winner.team_name,
                        "looser": looser.team_name,
                        "winner_score": winner.score,
                        "looser_score": looser.score,
                        "game_started": game["game_started_datetime"],
                        "game_finished": game_finished}

                file_name = "./files/{}_vs_{}_{}.yaml".format(winner.team_name, looser.team_name, game_finished)

                GameManager.save_game_results(file_name, data)

                self.send_message(self.teams[winner_name]["team_uid"], self.teams[winner_name]["team_chat_id"], u"Это победа! Ай малаца")
                self.send_message(self.teams[looser.team_name]["team_uid"], self.teams[looser.team_name]["team_chat_id"], u"Луууузеерыы! (Вы продули...=\)")

            if i >= 0:
                self.games = [g for g, j in enumerate(self.games) if j != i]

            try:
                del self.teams[team_name]
                del self.teams[opponent_name]
            except Exception as e:
                print "Exception while deleting teams {} and {} - {}".format(team_name, opponent_name, e.message)

        self.game_context.this_team = None
        self.game_context.opponent = None

        return SESSION_STOPPED_MSG.format(self.uid)

    #   game commands   ================================================================================================

    def remove_game_data(self, team_name=None):
        team_name = self.get_team_name() if not team_name else team_name
        self.games = [game for game in self.games
                      if game["team_name"] != team_name and game["opponent_team_name"] != team_name]

    def remove_team(self, team_name=None):
        team_name = self.get_team_name() if not team_name else team_name
        try:
            del self.teams[team_name]
            return True
        except Exception as e:
            print "Exception while deleting team {} - {}".format(team_name, e.message)
            return False

    def get_game_data(self, uid=None, team_name=None):
        team_name = self.get_team_name(uid) if not team_name else team_name
        if not team_name:
            return None, -1
        for i, game in enumerate(self.games):
            if game["team_name"] == team_name or game["opponent_team_name"] == team_name:
                return game, i
        return None, -1

    @need_game_session
    @need_game_started
    def check_winner(self):
        return self.game_context.check_winner()

    def get_game_winner(self):
        game, i = self.get_game_data()
        if game:
            return game["winner"]
        return ""

    def load(self):
        try:
            with open("./files/seabattle_game.yaml", 'r') as stream:
                data = yaml.load(stream)
                self.teams = data["teams"]
                self.games = data["games"]
                self.active_sessions = data["active_sessions"]
        except Exception as e:
            self.teams = {}
            self.games = []
            self.active_sessions = []
            print e.message

    def save(self):
        with open('./files/seabattle_game.yaml', 'w') as outfile:
            data = {"teams": self.teams, "games": self.games, "active_sessions": self.active_sessions}
            yaml.dump(data, outfile, default_flow_style=True)

    def session_is_active(self):
        if not self.uid or len(self.active_sessions) == 0:
            return False
        active = False
        try:
            for session in self.active_sessions:
                if session["session_uid"] == self.uid:
                    active = True
                    break
        except Exception as e:
            print "Exception occurred while checking session - {}".format(e.message)
            active = False
        return active

    def send_message(self, uid, chat_id, message):
        if chat_id:
            self.vk_user.send_message(text=message, userid=None, chatid=chat_id)
        else:
            self.vk_user.send_message(text=message, userid=uid, chatid=None)

    def start_game_with(self, op_team_name):
        found_game = None
        found_index = -1
        gc = self.game_context
        t_team_name = gc.this_team_name

        for i, game in enumerate(self.games):
            if game["game_started"]:
                continue
            # checking if this_team is awaited by some team
            if game["opponent_team_name"] == t_team_name and game["team_name"] != op_team_name:
                message = u"Команда {}, которую вы ожидали, играет с другой командой - выберите другого оппонента"
                team = self.teams[game["team_name"]]
                if team:
                    self.send_message(try_get_data(team, "team_uid"),
                                      try_get_data(team, "team_chat_id"),
                                      message)

            if game["opponent_team_name"] == t_team_name and game["team_name"] == op_team_name:
                found_game = game
                found_index = i

        if found_game and found_index >= 0:
            found_game["game_started"] = True
            found_game["winner"] = ""
            found_game["game_started_datetime"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.games[found_index] = found_game

            gc.op_team_name = op_team_name
            gc.opponent = GameContext.load_team_data(op_team_name)

            return GAME_STARTED_MSG.format(op_team_name)

        found_game = {"team_name": t_team_name,
                      "opponent_team_name": op_team_name,
                      "game_started": False,
                      "winner": "",
                      "game_started_datetime": None}
        self.games.append(found_game)
        return WAITING_FOR_OPPONENT_MSG.format(op_team_name)

    def is_answer_correct(self, answer, q_number):
        return answer == self.questions[q_number].values()[0]

    def question_answered(self, question_id, correct):
        gc = self.game_context
        if question_id in gc.this_team.answered_questions:
            return QUESTION_ALREADY_ANSWERED.format(question_id + 1)

        score_per_hit = 1 if correct else 0
        gc.this_team.score_per_hit = score_per_hit
        gc.this_team.answered_questions.append(question_id)

        if correct:
            return CORRECT_ANSWER_MSG.format(score_per_hit)
        return INVALID_ANSWER_TEXT_MSG

    def get_team_name(self, uid=None):
        uid = self.uid if not uid else uid
        for team_name in self.teams.keys():
            if self.teams[team_name]["team_uid"] == uid:
                return team_name
        return ""

    def get_opponent_name(self, team_name=None):
        team_name = self.game_context.this_team_name if not team_name else team_name
        if not team_name:
            return ""
        for game in self.games:
            if game["team_name"] == team_name:
                return game["opponent_team_name"]
            if game["opponent_team_name"] == team_name:
                return game["team_name"]
        return ""
