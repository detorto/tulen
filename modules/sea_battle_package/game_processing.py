#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import threading
import ship_processing as sp
from datetime import datetime
import os

# TODO: can this be different??
MAP_SIZE = 10

MAP_EXAMPLE = """
                0 0 0 1 0 0 3 0 0 1
                2 2 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 3 0 0 2
                0 0 1 0 0 0 0 0 0 2
                0 0 0 0 0 0 0 0 0 0
                0 0 4 4 4 4 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 3 3 3 0 1 0
                0 0 0 0 0 0 0 0 0 0
                """

TMP_TULEN_MAP = """
                0 0 0 1 0 0 3 0 0 1
                2 2 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 3 0 0 2
                0 0 1 0 0 0 0 0 0 2
                0 0 0 0 0 0 0 0 0 0
                0 0 4 4 4 4 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 3 3 3 0 1 0
                0 0 0 0 0 0 0 0 0 0
                """

# answers  ====================================================================
INVALID_ANSWER_FORMAT_MSG = u"Неправильный формат ответа"
INVALID_ANSWER_NUMBER_MSG = u"Неправильный номер ответа"
INVALID_ANSWER_TEXT_MSG = u"Неверный ответ!"

CORRECT_ANSWER_MSG = u"Ответ верен!"
WAITING_FOR_OPPONENT_MSG = u"Ждем оппонета"

UNKNOWN_TEAM = u"Неизвестная команда {}"
INVALID_OPPONENT_MSG = u"Неизветный противник"
CAN_SHOT_MSG = u"Могете стрелять, капитан"

NOT_REGISTERED_YET_MSG = u"Для игры в Морской Бой нужно зарегистрироватся. Напишите Я капитан команды ИМЯ_КОММАНДЫ"
NO_MAP_YET_MSG = u"Нужно загрузить карту. Напишите Загрузи карту [МАССИВ_КАРТЫ]\n" \
                 u"Подсказка: размер массива - 100 чисел подряд через пробел, число 0 - пустое место, числа 1-4 - корабли"
NO_OPPONENT_SET = u"Для игры нужно выбрать противника. Напишите Играю в морской бой с ИМЯ_КОМАНДЫ_ОППОНЕНТА"
NO_ANSWER_PROVIDED_MSG = u"Для выстрела нужно ответить на вопрос. Напишите Ответ на вопрос НОМЕР_ВОПРОСА: СЛОВО_ИЛИ_ЦИФРА"

ALREADY_REGISTERED = u"Уже зарегистрированы"
ALREADY_CAPTAIN = u"Вы уже являетесь капитаном"
# ALREADY_CHAT_REGISTERED = u"Из этого чата уже ведется игра"
TEAM_IS_WAITING_FOR_OPPONENT = u"Команда {} уже ожидает вас!"
TEAM_NOT_WAITING_FOR_ANY_OPPONENT = u"Команда {} не ожидает никаких оппонентов"
TEAM_NOT_WAITING_FOR_OPPONENT = u"Команда {} не ожидает оппонента {}, но ожидает {}"
TEAM_NAME_IS_EMPTY = u"Не могу зарегистрировать команду без имени!"
REGISTRATION_OK = u"Норм все, давай дальше"
OPPONENT_IS_ALREADY_SET = u"У команды (team_name {}, team_uid {}) уже есть оппонент (team_name {}, team_uid {})"
OPPONENT_SET_OK = u"Команде (team_name {}, team_uid {}) успешно выставлен оппонент (team_name {}, team_uid {})"

INVALID_MAP = u"Неверная карта"
GOOD_MAP = u"Карта загружена"
MAP_ALREADY_UPLOADED = u"Карта уже загружена"

SESSION_ALREADY_ACTIVE = u"Сессия игры уже активна для uid {}"
SESSION_STARTED = u"Сессия игры Морской Бой начата для uid {}"
SESSION_NOT_ACTIVE = u"Сессия не активна для uid {}"
SESSION_STOPPED = u"Сессия игры Морксой бой остановлена для uid {}"

# commands  ===================================================================
start_game_processing_command = u"тюлень, хотим в морской бой"
stop_game_processing_command = u"мы закончили морской бой"
answer_command = u"ответ"
gameRequest_command = u"играю в морской бой с"
attack_command = u"атакую:"
questions_command = u"вопросы"
loadMap_command = u"загрузи карту"
registerTeam_command = u"я капитан команды"

def need_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if game_manager.session_is_active():
            return f(*args)
        else:
            return
    return wrapper

def need_game_started(f):
    def wrapper(*args):
        game_context = args[0]
        if isinstance(game_context, GameManager):
            game_context = game_context.game_context
        if game_context.game_started:
            return f(*args)
        else:
            return
    return wrapper

def try_get_data(data, key):
    try:
        return data[key]
    except:
        return None


class Team:
    def __init__(self, cap_uid, team_name, score, field, field_of_shots, shots_left, score_per_hit,
                 answered_questions):
        self.cap_uid = cap_uid
        self.team_name = team_name
        self.score = score
        self.field = field
        self.field_of_shots = field_of_shots
        self.shots_left = shots_left
        self.score_per_hit = score_per_hit
        self.answered_questions = answered_questions
        self.field_parsed = False

        self.ships = {}
        for rank in sp.SHIP_RANKS_DICT:
            self.ships[rank] = []
            for ship in range(sp.SHIP_RANKS_DICT[rank]):
                self.ships[rank].append(sp.Ship(rank))
        # self.parse_fields()

    def can_play(self):
        not_ok = not self.cap_uid or not self.team_name or not self.field_parsed
        return not not_ok

    def parse_fields(self):
        self.field_parsed = False
        if self.field is None:
            return "Field is empty"
        if len(self.field) != MAP_SIZE * MAP_SIZE:
            print "parse_fields: map size is wrong = {}".format(len(self.field))
            return "Field size is wrong!"
        try:
            for i in range(MAP_SIZE):
                for j in range(MAP_SIZE):
                    was_hit = False
                    if self.field_of_shots is not None and len(self.field_of_shots) == len(self.field):
                        was_hit = self.field_of_shots[j + i * MAP_SIZE] == 'X'
                    point = sp.Point(i, j, int(self.field[j + i * MAP_SIZE]), was_hit)
                    for rank in sp.SHIP_RANKS_DICT:
                        for ship in self.ships[rank]:
                            try:
                                ship.add_point(point)
                            except sp.MapParseException as e:
                                print "Exception while parsing filed: {}".format(e.value)
                                return e.value
            self.field_parsed = True
            return "OK"
        except Exception as e:
            print "Exception occurred while parsing field for (cap_uid {}, team_name {}) - {}" \
                .format(self.cap_uid, self.team_name, e.message)
            return e.message

    @classmethod
    def try_serialize(cls, obj):
        try:
            if isinstance(obj, cls):
                return obj.serialize()
        except:
            pass
        return None

    def serialize(self):
        return {"cap_uid": self.cap_uid,
                "team_name": self.team_name,
                "score": self.score,
                "field": self.field,
                "field_of_shots": self.field_of_shots,
                "shots_left": self.shots_left,
                "score_per_hit": self.score_per_hit,
                "answered_questions": self.answered_questions}

    @classmethod
    def create_team(cls, data):
        if data is None:
            return None
        return cls(try_get_data(data, "cap_uid"),
                   try_get_data(data, "team_name"),
                   try_get_data(data, "score"),
                   try_get_data(data, "field"),
                   try_get_data(data, "field_of_shots"),
                   try_get_data(data, "shots_left"),
                   try_get_data(data, "score_per_hit"),
                   try_get_data(data, "answered_questions"))


class GameContext:
    def __init__(self, uid):
        self.uid = uid
        self.max_score = 1
        self.game_started = False
        self.game_started_dt_str = None
        self.this_team = None
        self.opponent = None
        self.load()

    def set_opponent(self, team_name, team_uid):
        if self.opponent is not None:
            return False
        op_data = {"cap_uid": team_uid,
                   "team_name": team_name,
                   "score": 0,
                   "field": [],
                   "field_of_shots": [],
                   "shots_left": 0,
                   "score_per_hit": 0,
                   "answered_questions": []}
        self.opponent = Team.create_team(op_data)
        return True

    @need_game_started
    def check_winner(self):
        t_score = self.this_team["score"]
        op_score = self.opponent["score"]
        if t_score >= self.max_score:
            return self.this_team["team_name"]
        if op_score >= self.max_score:
            return self.opponent["team_name"]
        return ""

    def load(self):
        try:
            with open("./files/seabattle_context_{}.yaml".format(self.uid), 'r') as stream:
                data = yaml.load(stream)
                self.max_score = data["max_score"]
                self.game_started = data["game_started"]
                self.game_started_dt_str = data["game_started_datetime"]
                self.this_team = Team.create_team(data["this_team"])
                self.opponent = Team.create_team(data["opponent"])
        except:
            self.max_score = 1
            self.game_started = False
            self.game_started_dt_str = None
            self.this_team = None
            self.opponent = None

    def save(self):
        print "Saving context for {}".format(self.uid)
        with open('./files/seabattle_context{}.yaml'.format(self.uid), 'w') as outfile:
            data = {"max_score": self.max_score,
                    "game_started": self.game_started,
                    "game_started_datetime": self.game_started_dt_str,
                    "this_team": Team.try_serialize(self.this_team),
                    "opponent": Team.try_serialize(self.opponent)}
            yaml.dump(data, outfile, default_flow_style=True)

    def is_valid(self):
        valid = self.this_team is not None \
                and self.this_team.can_play() \
                and self.opponent is not None \
                and self.opponent.can_play()
        return valid

class GameManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.games = []
        self.active_sessions = []
        self.load()

    def __call__(self, uid):
        self.uid = uid
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

    def load_map(self, field):
        self.game_context.this_team.field = field
        return self.game_context.this_team.parse_fields()

    def update_game_data(self, data):
        for i, game in enumerate(self.games):
            if game["team_name"] == data["team_name"]:
                game["team_uid"] = data["team_uid"]
                game["opponent_team_name"] = data["opponent_team_name"]
                game["opponent_uid"] = data["opponent_uid"]
                self.games[i] = game
                return True
        self.games.append(data)
        return False

    def remove_game_data(self, uid=None, team_name=None, opponent_name=None):
        game = self.get_game_data(uid, team_name, opponent_name)
        if game:
            # TODO: check!!!
            self.games.remove(game)
            return True
        return False

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
    def check_winner(self):
        return self.game_has_winner() or self.game_context.check_winner()

    @need_game_started
    def game_has_winner(self):
        gc = self.game_context
        game = self.get_game_data(team_name=gc.this_team["team_name"], opponent_name=gc.opponent["team_name"])
        winner = game["winner"]
        if not winner:
            return ""
        if winner != gc.this_team["team_name"] or winner != gc.opponent["team_name"]:
            print "Warning! game_has_winner: Somehow winner is not from this game! " \
                  "Check!!! t_team {}, op_team {}, winner {}"\
                .format(gc.this_team["team_name"], gc.opponent["team_name"], winner)
        return winner

    def load(self):
        try:
            with open("./files/seabattle_game.yaml", 'r') as stream:
                data = yaml.load(stream)
                self.games = data["games"]
                self.active_sessions = data["active_sessions"]
        except Exception as e:
            self.games = []
            self.active_sessions = []
            print e.message

    def save(self):
        with open('./files/seabattle_game.yaml', 'w') as outfile:
            data = {"games": self.games, "active_sessions": self.active_sessions}
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

    def start_game_session(self):
        if self.session_is_active():
            msg = SESSION_ALREADY_ACTIVE.format(self.uid)
            print msg
            return msg
        self.active_sessions.append({"session_uid": self.uid,
                                     "session_started": datetime.now().strftime("%d.%m.%Y %H:%M:%S")})
        msg = SESSION_STARTED.format(self.uid)
        print msg
        return msg

    def stop_game_session(self):
        if not self.session_is_active():
            # эта строка не должна вызываться, поскольку если сессии нету - команды морского боя не обрабатываются
            print SESSION_NOT_ACTIVE.format(self.uid)
            return False

        self.active_sessions = [session for session in self.active_sessions if session["session_uid"] != self.uid]
        return SESSION_STOPPED.format(self.uid)
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
                        print "Exception occured while saving game results for (winner {}, looser {}) - {}"\
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

    def is_team_registered(self, team_name):
        return self.get_game_data(team_name=team_name) is not None

    def is_user_registered(self, uid=None):
        return self.get_game_data(uid=uid) is not None

    # sets opponent by team_name for current team_name
    def set_opponent(self, op_team_name):
        gc = self.game_context
        t_team_name = gc.this_team["team_name"]
        t_cap_uid = gc.this_team["cap_uid"]
        if gc.opponent is not None:
            op_team_name = gc.opponent["team_name"]
            op_cap_uid = gc.opponent["cap_uid"]
            return OPPONENT_IS_ALREADY_SET.format(t_team_name,
                                                  t_cap_uid,
                                                  op_team_name,
                                                  op_cap_uid)
        for game in self.games:
            if game["team_name"] == op_team_name:
                op_cap_uid = game["team_uid"]
                self.game_context.set_opponent(op_team_name,
                                               op_cap_uid)

                # updating also game_manager team_data
                t_game_data = self.get_game_data()
                if t_game_data is None:
                    t_game_data = {"team_name": t_team_name,
                                   "team_uid": t_cap_uid}
                t_game_data["opponent_team_name"] = op_team_name
                t_game_data["opponent_uid"] = op_cap_uid
                self.update_game_data(t_game_data)
                return OPPONENT_SET_OK.format(t_team_name,
                                              t_cap_uid,
                                              op_team_name,
                                              op_cap_uid)
        return INVALID_OPPONENT_MSG

    def opponent_available(self, team_name=None, op_team_name=None):
        gc = self.game_context
        team_name = gc.this_team["team_name"] if team_name is None else team_name
        op_team_name = gc.this_team["team_name"] if op_team_name is None else op_team_name
        team = self.get_game_data(uid=None, team_name=team_name)
        if team is None:
            print UNKNOWN_TEAM.format(team_name)
            return False
        awaited_opponent = team["opponent_team_name"]
        if not awaited_opponent:
            print TEAM_NOT_WAITING_FOR_ANY_OPPONENT.format(team_name)
            return False
        if awaited_opponent != op_team_name:
            print TEAM_NOT_WAITING_FOR_OPPONENT.format(team_name, op_team_name, awaited_opponent)
            return False
        return True

    def register_team(self, uid, team_name):
        print u"registering sea_battle team {} with captain uid {}".format(team_name, uid)
        if not team_name:
            return TEAM_NAME_IS_EMPTY

        ans = REGISTRATION_OK
        found_opponent = False

        for game in self.games:
            if game["team_name"] == team_name:
                return ALREADY_REGISTERED
            if game["team_uid"] == uid:
                return ALREADY_CAPTAIN
            # TODO: check!!!!

            if game["opponent_team_name"] == team_name:
                if game["opponent_uid"] is not None:
                    if game["opponent_uid"] != uid:
                        ans = ALREADY_REGISTERED
                    else:
                        ans = ALREADY_CAPTAIN
                else:
                    game["opponent_uid"] = uid

                ans += "\n" + TEAM_IS_WAITING_FOR_OPPONENT.format(game["team_name"])
                found_opponent = True
                self.update_game_data(game)
                break

        if not found_opponent:
            self.update_game_data({"team_name": team_name,
                                   "team_uid": uid,
                                   "opponent_team_name": None,
                                   "opponent_uid": None})
        return ans
