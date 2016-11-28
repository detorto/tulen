#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import enum
from ast import literal_eval as make_tuple
from game_constants import MAP_SIZE

Orientations = enum('Horizontal', 'Vertical')

SHIP_RANKS_DICT = {1: 4, 2: 3, 3: 2, 4: 1}


class Point:
    def __init__(self, x, y, value, was_hit):
        self.x = x
        self.y = y
        self.value = value
        self.was_hit = was_hit

    @classmethod
    def try_parse(cls, coords_str):
        try:
            coords_str = "(" + coords_str + ")"
            point_t = make_tuple(coords_str)
            if not point_t[0] in range(0, MAP_SIZE):
                return u"Первая координата точки {} не верна! Координаты должны быть от 0 до {}"\
                    .format(coords_str, MAP_SIZE)
            if not point_t[1] in range(0, MAP_SIZE):
                return u"Вторая координата точки {} не верна! Координаты должны быть от 0 до {}"\
                    .format(coords_str, MAP_SIZE)
            return cls(point_t[0], point_t[1], -1, -1)
        except Exception as e:
            print "Error!! Couldn't parse a point from coordinates! - {}".format(e.message)
            return None

    def __str__(self):
        return u"Point ({}, {}) with value {}".format(self.x, self.y, self.value)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)


class MapParseException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return u"Map parsing error - " + str(self.value)


class Ship:
    def __init__(self, rank):
        self.rank = rank
        self.points = []
        # self.hit_points = hit_points
        self.orientation = None

    def __str__(self):
        points_str = u""
        for p in self.points:
            points_str += str(p)
        return u"Ship ({}) with rank = {}, orientation = {}, full_load = {}" \
            .format(points_str, self.rank, str(self.orientation), str(len(self.points) == self.rank))

    def check_dead(self):
        for p in self.points:
            if not p.was_hit:
                return False
        return True

    def try_attack(self, hit_point):
        for i, p in enumerate(self.points):
            if p == hit_point:
                if p.was_hit:
                    return u"Вы сюда ужо стреляли, повнимательней"
                p.was_hit = True
                self.points[i] = p
                if self.check_dead():
                    return u"Корабль подбит!"
                return u"Ай малаца, попал! (корабль ещё жив)"
        return None

    @staticmethod
    def get_points_orientation(p2, p1):
        if p2.x in range(p1.x - 1, p1.x + 1, 2) and p2.y in range(p1.y - 1, p1.y + 1, 2):
            # skewed orientations ain't supported!
            return None
        if p2.x in range(p1.x - 1, p1.x + 1, 2):
            return Orientations.Horizontal
        if p2.y in range(p1.y - 1, p1.y + 1, 2):
            return Orientations.Vertical
        return None

    def can_place_point(self, point, p):
        orientation = self.get_points_orientation(point, p)
        if orientation is None:
            return None
        if self.orientation and self.orientation != orientation:
            return None
        return orientation

    def this_ship_point(self, point):
        if point.value != self.rank:
            return False

        for p in self.points:
            orientation = self.can_place_point(point, p)
            if orientation is not None:
                self.orientation = orientation
                break
        return True

    def can_place_another_ship(self, point):
        for p in self.points:
            if point.x in range(p.x - 1, p.x + 1, 2) and point.y in range(p.y - 1, p.y + 1, 2):
                return False
        return True

    def add_point(self, point):
        if self.this_ship_point(point):
            if len(self.points) >= self.rank:
                raise MapParseException("too many points in ship {} for rank - {}".format(str(self)))
            self.points.append(point)
            return True

        if not self.can_place_another_ship(point):
            raise MapParseException("another ship's point {} is too close to this ship {}".format(point, str(self)))
        return False
