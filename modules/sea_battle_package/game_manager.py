#!/usr/bin/python
# -*- coding: utf-8 -*-

from game_context import *
from datetime import datetime
import threading
import os


class GameManager:
    def __init__(self, vk_user, questions):
        self.lock = threading.Lock()
        self.vk_user = vk_user
        self.questions = questions

        self.teams = {}
        self.games = []
        self.active_sessions = []

        self.load()

    def __call__(self, uid, chat_id):
        self.uid = uid
        self.chat_id = chat_id
        self.load()
        self.game_context = GameContext(uid)
        if self.check_winner():
            self.stop_game_session()

        return self

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
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
    @need_not_registered
    def register_team(self, message):
        # from forth word
        team_name = "".join(message.split()[3:]).strip()

        self.teams[team_name] = {"team_uid": self.uid, "team_chat_id": self.chat_id}
        self.game_context.create_this_team(team_name, self.uid)

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
        op_team_name = message.split(gameRequest_command, 1)[1:][0].strip()

        if op_team_name not in self.teams:
            return UNKNOWN_TEAM_MSG.format(op_team_name)

        return self.start_game_with(op_team_name)

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
        pass

    @need_game_session
    def stop_game_session(self, message=""):
        self.active_sessions = [session for session in self.active_sessions if session["session_uid"] != self.uid]

        # TODO: process game ending and winner!!!!

        team_name = self.game_context.this_team.team_name if self.game_context.this_team else ""
        for t_name in self.teams.keys():
            if self.teams[t_name]["team_uid"] == self.uid:
                team_name = t_name
                break

        if team_name:
            try:
                del self.teams[team_name]
            except Exception as e:
                print "Exception while deleting team {} - {}".format(team_name, e.message)
                pass

            self.games = [game for game in self.games if game["team_name"] != team_name]
            for game in self.games:
                if game["opponent_team_name"] == team_name:
                    game["opponent_team_name"] = ""
                    # TODO: change!!!
                    game["winner"] = game["team_name"]
        self.game_context.this_team = None
        self.game_context.opponent = None

        return SESSION_STOPPED_MSG.format(self.uid)
        # TODO: tmp - debug

        if self.game_context.game_started:
            gc = self.game_context
            winner_team = gc.check_winner()
            if not winner_team:
                # no player yet achieved max_score
                winner_team = self.game_has_winner()
                # checking if another team at it's session already wrote down the winner
                if not winner_team:
                    # if it's not, then this team has stopped the game and the winner is opponent!
                    winner_team = gc.opponent["team_name"]
                    looser_team = gc.this_team["team_name"]
                    winner_score = gc.opponent["score"]
                    looser_score = gc.this_team["score"]
                    game_started = gc.game_started_dt_str
                    game_finished = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    file_name = "./files/{}_vs_{}_{}.yaml".format(winner_team, looser_team, game_finished)
                    try:
                        with open(file_name, 'w') as outfile:
                            data = {"winner": winner_team,
                                    "looser": looser_team,
                                    "winner_score": winner_score,
                                    "looser_score": looser_score,
                                    "game_started": game_started,
                                    "game_finished": game_finished}
                            yaml.dump(data, outfile, default_flow_style=True)
                    except Exception as e:
                        print "Exception occured while saving game results for (winner {}, looser {}) - {}" \
                            .format(winner_team, looser_team, e.message)

                    try:
                        os.remove("./files/seabattle_context{}.yaml".format(gc.uid))
                    except Exception as e:
                        print e.message
                    # TODO: delete context file and game data from seabattle_game before return!!!
                    if not self.remove_game_data(team_name=looser_team, opponent_name=winner_team):
                        print "Warning: was unable to remove game data from storage - check!!!"
                    return True
                else:
                    game = self.get_game_data(team_name=winner_team)
                    pass
                    # TODO: tell user, that opponent has finished the game and this team is a winner (apparently)
                    # TODO: delete context file and game data from seabattle_game before return!!!
            else:
                pass
                # TODO: we have a winner by scores! And we have to check it earlier, actually...
                # TODO: delete context file and game data from seabattle_game before return!!!
        else:
            pass
            # TODO: game ain't started - we can safely delete all data and tell user, that session is successfully finished
            # TODO: delete context file and game data from seabattle_game before return!!!


            # если какой-то игрок покинул игру до окончания игры (score < max_score), победа присуждается другому игроку
            # сохраняем в файлик {this_team_name}_vs_{opponent_team_name}_{datetime.now()}.yaml
            # После чего, удаляем seabattle_context_{cap_uid}.yaml, удаляем только this_team из self.games,
            # удаляем текущую сессию из self.active_sessions
            # Сохраняемся.
            # если игра не началась ещё - делаем всё то же самое, но ничего не сохраняем

    #   game commands   ================================================================================================

    # def update_game_data(self, data):
    #     for i, game in enumerate(self.games):
    #         if game["team_name"] == data["team_name"]:
    #             game["opponent_team_name"] = try_get_data(data, "opponent_team_name")
    #             game["game_started"] = try_get_data(data, "game_started")
    #             game["winner"] = try_get_data(data, "winner")
    #             self.games[i] = game
    #             return True
    #     self.games.append(data)
    #     try:
    #         self.game_context.create_this_team(data["team_name"], data["team_uid"])
    #     except Exception as e:
    #         print "Exception occured while setting this_team data context - {}".format(e.message)
    #     return False

    # def remove_game_data(self, uid=None, team_name=None, opponent_name=None):
    #     game = self.get_game_data(uid, team_name, opponent_name)
    #     if game:
    #         # TODO: check!!!
    #         self.games.remove(game)
    #         return True
    #     return False

    def get_game_data(self, uid=None, team_name=None, opponent_name=None):
        m_uid = self.uid if uid is None else uid
        for game in self.games:
            if team_name is not None:
                if opponent_name is not None:
                    if game["team_name"] == team_name and game["opponent_team_name"] == opponent_name:
                        return game
                if game["team_name"] == team_name:
                    return game
            elif game["team_uid"] == m_uid:
                return game
        return None

    @need_game_session
    @need_game_started
    def check_winner(self):
        return self.game_has_winner() or self.game_context.check_winner()

    def game_has_winner(self):
        gc = self.game_context
        game = self.get_game_data(team_name=gc.this_team["team_name"], opponent_name=gc.opponent["team_name"])
        winner_team_name = game["winner"]
        if not winner_team_name:
            return ""
        if winner_team_name != gc.this_team["team_name"] or winner_team_name != gc.opponent["team_name"]:
            print "Warning! game_has_winner: Somehow winner is not from this game! " \
                  "Check!!! t_team {}, op_team {}, winner {}" \
                .format(gc.this_team["team_name"], gc.opponent["team_name"], winner_team_name)
        return winner_team_name

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

    def is_team_registered(self):
        if not self.game_context.this_team:
            return False
        team_name = self.game_context.this_team.team_name if self.game_context.this_team else ""
        if not team_name:
            return False
        return team_name in self.teams

    def send_message(self, uid, chat_id, message):
        if chat_id:
            self.vk_user.send_message(text=message, userid=None, chatid=chat_id)
        else:
            self.vk_user.send_message(text=message, userid=uid, chatid=None)

    def start_game_with(self, op_team_name):
        gc = self.game_context
        team_name = gc.this_team["team_name"]

        found_game = None
        found_index = -1

        for i, game in enumerate(self.games):
            if game["opponent_team_name"] == team_name and game["team_name"] != op_team_name:
                message = u"Команда {}, которую вы ожидали, играет с другой командой - выберите другого оппонента"
                team = self.teams[game["team_name"]]
                if team:
                    self.send_message(try_get_data(team, "team_uid"),
                                      try_get_data(team, "team_chat_id"),
                                      message)

            if game["opponent_team_name"] == team_name and game["team_name"] == op_team_name:
                found_game = game
                found_index = i

        if found_game and found_index >= 0:
            found_game["game_started"] = True
            found_game["winner"] = ""
            found_game["game_started_datetime"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.games[found_index] = found_game

            return GAME_STARTED_MSG.format(op_team_name)

        found_game = {"team_name": team_name,
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
