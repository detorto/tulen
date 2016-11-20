#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import threading
import ship_processing as sp
from datetime import datetime

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
NO_MAP_YET_MSG = u"Нужно загрузить карту"
ALREADY_REGISTERED = u"Уже зарегистрированы"
ALREADY_CAPTAIN = u"Вы уже являетесь капитаном"
ALREADY_CHAT_REGISTERED = u"Из этого чата уже ведется игра"
TEAM_IS_WAITING_FOR_OPPONENT = u"Команда {} уже ожидает вас!"
TEAM_NOT_WAITING_FOR_ANY_OPPONENT = u"Команда {} не ожидает никаких оппонентов"
TEAM_NOT_WAITING_FOR_OPPONENT = u"Команда {} не ожидает оппонента {}, но ожидает {}"
TEAM_NAME_IS_EMPTY = u"Не могу зарегистрировать команду без имени!"
REGISTRATION_OK = u"Норм все, давай дальше"
OPPONENT_IS_ALREADY_SET = u"У команды (team_name {}, team_uid {}, team_chat_id {}) уже есть оппонент (team_name {}, team_uid {}, team_chat_id {})"
OPPONENT_SET_OK = u"Команде (team_name {}, team_uid {}, team_chat_id {}) успешно выставлен оппонент (team_name {}, team_uid {}, team_chat_id {})"

INVALID_MAP = u"Неверная карта"
GOOD_MAP = u"Карта загружена"
MAP_ALREADY_UPLOADED = u"Карта уже загружена"

SESSION_ALREADY_ACTIVE = u"Сессия игры уже активна для uid {}, chat_id {}"
SESSION_STARTED = u"Сессия игры Морской Бой начата для uid {}, chat_id {}"
SESSION_NOT_ACTIVE = u"Сессия не активна для uid {}, chat_id {}"

# commands  ===================================================================
start_game_processing_command = u"тюлень, хотим в морской бой"
stop_game_processing_command = u"мы закончили морской бой"
answer_command = u"ответ"
gameRequest_command = u"играю в морской бой с"
attack_command = u"атакую:"
questions_command = u"вопросы"
loadMap_command = u"загрузи карту"
registerTeam_command = u"я капитан команды"


def try_get_data(data, key):
    try:
        return data[key]
    except:
        return None

def check_null_or_empty(data):
    if isinstance(data, (int, long)):
        return data == 0
    elif isinstance(data, str):
        return data == ""
    return data is None


class Team:
    def __init__(self, cap_uid, chat_id, team_name, score, field, field_of_shots, shots_left, score_per_hit,
                 answered_questions):
        self.cap_uid = cap_uid
        self.chat_id = chat_id
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
        not_ok = check_null_or_empty(self.cap_uid) or check_null_or_empty(self.team_name) or not self.field_parsed
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
            print "Exception occurred while parsing field for (cap_uid {}, chat_id {}, team_name {}) - {}" \
                .format(self.cap_uid, self.chat_id, self.team_name, e.message)
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
                "chat_id": self.chat_id,
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
                   try_get_data(data, "chat_id"),
                   try_get_data(data, "team_name"),
                   try_get_data(data, "score"),
                   try_get_data(data, "field"),
                   try_get_data(data, "field_of_shots"),
                   try_get_data(data, "shots_left"),
                   try_get_data(data, "score_per_hit"),
                   try_get_data(data, "answered_questions"))


class GameContext:
    def __init__(self, uid, chat_id):
        self.uid = uid
        self.chat_id = chat_id
        self.max_score = 1
        self.game_started = False
        self.this_team = None
        self.opponent = None
        self.load()

    def set_opponent(self, team_name, team_uid, team_chat_id):
        if self.opponent is not None:
            return False
        op_data = {"cap_uid": team_uid,
                   "chat_id": team_chat_id,
                   "team_name": team_name,
                   "score": 0,
                   "field": [],
                   "field_of_shots": [],
                   "shots_left": 0,
                   "score_per_hit": 0,
                   "answered_questions": []}
        self.opponent = Team.create_team(op_data)
        return True

    def load(self):
        try:
            with open("./files/seabattle_context_{}.yaml".format(self.uid), 'r') as stream:
                data = yaml.load(stream)
                self.max_score = data["max_score"]
                self.game_started = data["game_started"]
                self.this_team = Team.create_team(data["this_team"])
                self.opponent = Team.create_team(data["opponent"])
                # self.game_in_progress = True
        except:
            self.max_score = 1
            self.game_started = False
            self.this_team = None
            self.opponent = None
            # self.this_team = Team.create_team({""})
            # self.game_in_progress = False

    def save(self):
        print "Saving context for {}".format(self.uid)
        with open('./files/seabattle_context{}.yaml'.format(self.uid), 'w') as outfile:
            data = {"max_score": self.max_score,
                    "game_started": self.game_started,
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
        self.teams = []
        self.active_sessions = []
        self.load()

    def __call__(self, uid, chat_id):
        self.uid = uid
        self.chat_id = chat_id
        self.load()
        self.game_context = GameContext(uid, chat_id)

        return self

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
        self.save()
        self.game_context.save()
        self.lock.release()

    def update_team_data(self, data):
        for i, item in enumerate(self.teams):
            if item["team_name"] == data["team_name"]:
                item["team_uid"] = data["team_uid"]
                item["team_chat_id"] = data["team_chat_id"]
                item["opponent_team_name"] = data["opponent_team_name"]
                item["opponent_uid"] = data["opponent_uid"]
                item["opponent_chat_id"] = data["opponent_chat_id"]
                self.teams[i] = item
                return True
        self.teams.append(data)
        return False

    def get_team_data(self, uid=None, chat_id=None, team_name=None):
        m_uid = self.uid if uid is None else uid
        m_chat_id = self.chat_id if chat_id is None else chat_id
        for team in self.teams:
            if team_name is not None:
                if team["team_name"] == team_name:
                    return team
            elif team["team_uid"] == m_uid and team["team_chat_id"] == m_chat_id:
                return team
        return None

    def load(self):
        try:
            with open("./files/seabattle_game.yaml", 'r') as stream:
                data = yaml.load(stream)
                self.teams = data["teams"]
                self.active_sessions = data["active_sessions"]
        except Exception as e:
            self.teams = []
            self.active_sessions = []
            print e.message

    def save(self):
        with open('./files/seabattle_game.yaml', 'w') as outfile:
            data = {"teams": self.teams, "active_sessions": self.active_sessions}
            yaml.dump(data, outfile, default_flow_style=True)

    def session_is_active(self):
        if self.uid is None or len(self.active_sessions) == 0:
            return False
        active = False
        try:
            for session in self.active_sessions:
                active = session["session_uid"] == self.uid
                if active and session["session_chat_id"] is not None:
                    active = session["session_chat_id"] == self.chat_id
                if active:
                    break
        except Exception as e:
            print "Exception occurred while checking session - {}".format(e.message)
            active = False
        return active

    def start_game_session(self):
        if self.session_is_active():
            return SESSION_ALREADY_ACTIVE.format(self.uid, self.chat_id)
        self.active_sessions.append({"session_uid": self.uid,
                                     "session_chat_id": self.chat_id,
                                     "session_started": datetime.now().strftime("%d.%m.%Y %H:%M:%S")})
        return SESSION_STARTED.format(self.uid, self.chat_id)

    def stop_game_session(self):
        if not self.session_is_active():
            # эта строка не должна вызываться, поскольку если сессии нету - команды морского боя не обрабатываются
            return SESSION_NOT_ACTIVE.format(self.uid, self.chat_id)
        if self.game_context.game_started:
            pass
            # если какой-то игрок покинул игру до окончания игры (score < max_score), победа присуждается другому игроку
            # сохраняем в файлик {this_team_name}_vs_{opponent_team_name}_{datetime.now()}.yaml
            # После чего, удаляем seabattle_context_{cap_uid}.yaml, удаляем только this_team из self.teams,
            # удаляем текущую сессию из self.active_sessions
            # Сохраняемся.
            # если игра не началась ещё - делаем всё то же самое, но ничего не сохраняем

    def is_team_registered(self, team_name):
        return self.get_team_data(None, None, team_name) is not None

    def is_user_registered(self, uid=None, chat_id=None):
        return self.get_team_data(uid, chat_id) is not None

    # sets opponent by team_name for current team_name
    def set_opponent(self, op_team_name):
        gc = self.game_context
        t_team_name = gc.this_team["team_name"]
        t_cap_uid = gc.this_team["cap_uid"]
        t_chat_id = gc.this_team["chat_id"]
        if gc.opponent is not None:
            op_team_name = gc.opponent["team_name"]
            op_cap_uid = gc.opponent["cap_uid"]
            op_chat_id = gc.opponent["chat_id"]
            return OPPONENT_IS_ALREADY_SET.format(t_team_name,
                                                  t_cap_uid,
                                                  t_chat_id,
                                                  op_team_name,
                                                  op_cap_uid,
                                                  op_chat_id)
        for team in self.teams:
            if team["team_name"] == op_team_name:
                op_cap_uid = team["team_uid"]
                op_chat_id = team["team_chat_id"]
                self.game_context.set_opponent(op_team_name,
                                               op_cap_uid,
                                               op_chat_id)

                # updating also game_manager team_data
                this_team_data = self.get_team_data()
                if this_team_data is None:
                    this_team_data = {"team_name": t_team_name,
                                      "team_uid": t_cap_uid,
                                      "team_chat_id": t_chat_id}
                this_team_data["opponent_team_name"] = op_team_name
                this_team_data["opponent_uid"] = op_cap_uid
                this_team_data["opponent_chat_id"] = op_chat_id
                self.update_team_data(this_team_data)
                return OPPONENT_SET_OK.format(t_team_name,
                                              t_cap_uid,
                                              t_chat_id,
                                              op_team_name,
                                              op_cap_uid,
                                              op_chat_id)
        return INVALID_OPPONENT_MSG

    def opponent_available(self, team_name=None, op_team_name=None):
        team_name = self.game_context.this_team["team_name"] if team_name is None else team_name
        op_team_name = self.game_context.this_team["team_name"] if op_team_name is None else op_team_name
        team = self.get_team_data(None, None, team_name)
        if team is None:
            print UNKNOWN_TEAM.format(team_name)
            return False
        awaited_opponent = team["opponent_team_name"]
        if check_null_or_empty(awaited_opponent):
            print TEAM_NOT_WAITING_FOR_ANY_OPPONENT.format(team_name)
            return False
        if awaited_opponent != op_team_name:
            print TEAM_NOT_WAITING_FOR_OPPONENT.format(team_name, op_team_name, awaited_opponent)
            return False
        return True

    def register_team(self, uid, chat_id, team_name):
        print u"registering sea_battle team {} with captain uid {} and chat_id {}".format(team_name, uid,
                                                                                          chat_id)
        if check_null_or_empty(team_name):
            return TEAM_NAME_IS_EMPTY

        ans = REGISTRATION_OK
        found_opponent = False

        for team in self.teams:
            if team["team_name"] == team_name:
                return ALREADY_REGISTERED
            if team["team_uid"] == uid:
                return ALREADY_CAPTAIN
            # TODO: check!!!!
            if team["team_chat_id"] is not None and chat_id is not None and team["team_chat_id"] == chat_id:
                return ALREADY_CHAT_REGISTERED

            if team["opponent_team_name"] == team_name:
                if team["opponent_uid"] is not None:
                    if team["opponent_uid"] != uid:
                        ans = ALREADY_REGISTERED
                    else:
                        ans = ALREADY_CAPTAIN
                else:
                    team["opponent_uid"] = uid
                    team["opponent_chat_id"] = chat_id

                ans += "\n" + TEAM_IS_WAITING_FOR_OPPONENT.format(team["team_name"])
                found_opponent = True
                self.update_team_data(team)
                break

        if not found_opponent:
            self.update_team_data({"team_name": team_name,
                                   "team_uid": uid,
                                   "team_chat_id": chat_id,
                                   "opponent_team_name": None,
                                   "opponent_uid": None,
                                   "opponent_chat_id": None})
        return ans

        # def score_answer(self, q_number):
        #     pass
        #     # print "Scored answer {}".format(q_number)
        #     # self.scores.append(q_number)
        #
        # def score_hit(self, coords):
        #     pass
        #
        # def map_text(self):
        #     txt = ""
        #     for i in range(MAP_SIZE):
        #         for j in range(MAP_SIZE):
        #             txt += self.field[j + i * MAP_SIZE]
        #         txt += "\n"
        #     return txt
        #
        # def is_map_valid(self, data):
        #     pass
        # if data and len(data) == MAP_SIZE * MAP_SIZE:
        #     return True
        # else:
        #     return False

        # def set_map(self, data):
        #     if self.game_in_progress:
        #         return MAP_ALREADY_UPLOADED
        #     try:
        #         self.field = []
        #         for i in range(MAP_SIZE):
        #             for j in range(MAP_SIZE):
        #                 self.field.append(data[j + i * MAP_SIZE])
        #                 self.fieldM[i][j] = data[j + i * MAP_SIZE]
        #
        #         if self.is_map_valid(self.field):
        #             return GOOD_MAP + u"\n" + self.map_text()
        #         else:
        #             return INVALID_MAP
        #     except:
        #         return INVALID_MAP


def need_registration(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        if game_manager.is_user_registered():
            return f(*args)
        else:
            return NOT_REGISTERED_YET_MSG
    return wrapper

def need_valid_context(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.is_valid():
            return f(*args)
        else:
            return NO_MAP_YET_MSG
    return wrapper

def need_valid_map(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.is_valid():
            return f(*args)
        else:
            return NO_MAP_YET_MSG
    return wrapper

def need_game_started(f):
    def wrapper(*args):
        game_manager = args[0].game_manager
        game_context = game_manager.game_context
        if game_context.game_started:
            return f(*args)
        else:
            return NO_MAP_YET_MSG
    return wrapper
