#!/usr/bin/python
# -*- coding: utf-8 -*-

import ship_processing as sp
from utils import *


class Team:
    def __init__(self, cap_uid, team_name, op_team_name, op_cap_uid, score, field, field_of_shots,
                 shots_left, score_per_hit, question_answered, answered_questions):
        self.cap_uid = cap_uid if cap_uid else ""
        self.team_name = team_name if team_name else ""
        self.score = score if score else 0
        self.field = field if field else []
        self.field_of_shots = field_of_shots if field_of_shots else []
        self.shots_left = shots_left if shots_left else 0
        self.score_per_hit = score_per_hit if score_per_hit else 0
        self.question_answered = question_answered if question_answered else False
        self.answered_questions = answered_questions if answered_questions else []
        self.field_parsed = False

        self.ships = {}
        for rank in sp.SHIP_RANKS_DICT:
            self.ships[rank] = []
            for ship in range(sp.SHIP_RANKS_DICT[rank]):
                self.ships[rank].append(sp.Ship(rank))

    def parse_fields(self):
        self.field_parsed = False
        if self.field is None:
            return u"Поле пустое"
        if len(self.field) != MAP_SIZE * MAP_SIZE:
            print "parse_fields: map size is wrong = {}".format(len(self.field))
            return "Field size is wrong!"
        try:
            for i in range(MAP_SIZE):
                for j in range(MAP_SIZE):
                    was_hit = False
                    if self.field_of_shots is not None and len(self.field_of_shots) == len(self.field):
                        # _ for unknown cell, . for missed shot, X for hit ship
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
                "question_answered": self.question_answered,
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
                   try_get_data(data, "question_answered"),
                   try_get_data(data, "answered_questions"))