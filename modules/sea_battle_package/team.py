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
        for rank in sp.SHIP_RANKS_DICT:
            self.ships[rank] = []
            for ship in range(sp.SHIP_RANKS_DICT[rank]):
                self.ships[rank].append(sp.Ship(rank))
                self.ships_count += 1

    def parse_fields(self, field):
        self.field_parsed = False
        if field is None:
            return u"Поле пустое"
        if len(field) != MAP_SIZE * MAP_SIZE:
            print "parse_fields: map size is wrong = {}".format(len(self.field))
            return u"Размер поля не верен! Должно быть ровно {} точек".format(MAP_SIZE * MAP_SIZE)
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
                            except sp.MapParseException as e:
                                print "Exception while parsing filed: {}".format(e.value)
                                return e.value
                        if point_added:
                            break
                        elif point.value == rank:
                            return u"Кораблей ранга {} слишком много!".format(rank)

            if ships_filled != self.ships_count:
                return u"Не удалось расставить все корабли! Проверьте ваше поле на наличие всех необходимых кораблей"

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