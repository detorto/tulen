#!/usr/bin/python
# -*- coding: utf-8 -*-

import ship_processing as sp
from utils import *

def generate_field_of_shots():
    return ['_' for i in range(MAP_SIZE*MAP_SIZE)]


class Team:
    def __init__(self, cap_uid, team_name, score, field, field_of_shots,
                 shots_left, score_per_hit, question_answered, answered_questions):
        self.cap_uid = cap_uid if cap_uid else ""
        self.team_name = team_name if team_name else ""
        self.score = score if score else 0
        self.field = field if field else []
        self.field_of_shots = field_of_shots if field_of_shots and len(field_of_shots) else generate_field_of_shots()
        self.shots_left = shots_left if shots_left else 0
        self.score_per_hit = score_per_hit if score_per_hit else 0
        self.question_answered = question_answered if question_answered else False
        self.answered_questions = answered_questions if answered_questions else []

        self.field_parsed = False
        self.ships = {}
        self.ships_count = 0
        self.points = []

    @staticmethod
    def get_ship_instruction():
        msg = u"На карте должны быть расставлены корабли следующих рангов:\n"
        for rank in sp.SHIP_RANKS_DICT:
            msg += u"Ранг {} - {} корабля(-ь)\n".format(rank, sp.SHIP_RANKS_DICT[rank])
        msg += u"Ранг означает количество точек в корабле, а также номиналы этих точек.\n" \
               u"То есть, если корабль ранга 3, " \
               u"вам нужно разместить на поле подряд 3 цифры 3 по горизонтали или вертикали."
        return msg

    def get_alive_ships_count(self):
        if not self.field_parsed:
            return -1
        count = 0
        for rank in sp.SHIP_RANKS_DICT:
            for ship in self.ships[rank]:
                if not ship.check_dead():
                    count += 1
        return count

    def clear_ships(self):
        self.field_parsed = False
        self.ships = {}
        self.ships_count = 0
        for rank in sp.SHIP_RANKS_DICT:
            self.ships[rank] = []
            for ship in range(sp.SHIP_RANKS_DICT[rank]):
                self.ships[rank].append(sp.Ship(rank))
                self.ships_count += 1
        self.points = []

    # prints either self field merged with shots made at this field
    # or only field of shots
    def print_fields(self, only_shots):
        field = u""
        to_print = self.field_of_shots

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                printed = not only_shots

                if not only_shots:
                    printed = to_print[j + i * MAP_SIZE] == '_' and self.field[j + i * MAP_SIZE] != '0'
                    if printed:
                        field += str(self.field[j + i * MAP_SIZE]) + u"\t"

                if not printed:
                    field += to_print[j + i * MAP_SIZE] + u"\t"

            field += u"\n"
        return field

    def parse_fields(self, field):
        self.clear_ships()
        if field is None:
            return u"Поле пустое"
        if len(field) != MAP_SIZE * MAP_SIZE:
            print "parse_fields: map size is wrong = {}".format(len(self.field))
            msg = u"Размер поля не верен! Должно быть ровно {} точек\n".format(MAP_SIZE * MAP_SIZE)
            msg += Team.get_ship_instruction()
            return msg
        try:
            ships_filled = 0
            for i in range(MAP_SIZE):
                for j in range(MAP_SIZE):
                    was_hit = False
                    if self.field_of_shots is not None and len(self.field_of_shots) == len(field):
                        # _ for unknown cell, . for missed shot, X for hit ship
                        was_hit = self.field_of_shots[j + i * MAP_SIZE] == 'X'
                    point = sp.Point(j, i, int(field[j + i * MAP_SIZE]), was_hit)
                    if not point.value:
                        continue
                    for rank in sp.SHIP_RANKS_DICT:
                        point_added = False
                        for ship in self.ships[rank]:
                            try:
                                if ship.add_point(point):
                                    point_added = True
                                    if ship.is_full():
                                        ships_filled += 1
                                    break
                            except Exception as e:
                                if isinstance(e, sp.MapParseException):
                                    return e.value
                                print "Exception while parsing filed: {}".format(e.message)
                                return e.message
                        if point_added:
                            self.points.append(point)
                            break
                        elif point.value == rank:
                            return u"Кораблей ранга {} слишком много!".format(rank)

            if ships_filled != self.ships_count:
                msg = u"Не удалось расставить все корабли! " \
                       u"Проверьте ваше поле на наличие всех необходимых кораблей и точек в них\n"
                msg += Team.get_ship_instruction()
                return msg

            self.field_parsed = True
            self.field = field
            return GOOD_MAP_MSG
        except Exception as e:
            print "Exception occurred while parsing field - {}" \
                .format(e.message)
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
                "question_answered": self.question_answered,
                "answered_questions": self.answered_questions}

    @classmethod
    def create_team(cls, data):
        if not data:
            return None
        return cls(try_get_data(data, "cap_uid"),
                   try_get_data(data, "team_name"),
                   try_get_data(data, "score"),
                   try_get_data(data, "field"),
                   try_get_data(data, "field_of_shots"),
                   try_get_data(data, "shots_left"),
                   try_get_data(data, "score_per_hit"),
                   try_get_data(data, "question_answered"),
                   try_get_data(data, "answered_questions"))