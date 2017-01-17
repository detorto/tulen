#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import Orientation
from ast import literal_eval as make_tuple
from game_constants import *

SHIP_RANKS_DICT = {1: 4, 2: 3, 3: 2, 4: 1}


class Point:
    def __init__(self, x, y, value, was_hit):
        self.x = x
        self.y = y
        self.value = value
        self.was_hit = was_hit

    @staticmethod
    def fits_field(point):
        return 0 <= point.x < MAP_SIZE and 0 <= point.y < MAP_SIZE

    @classmethod
    def try_parse(cls, coords_str):
        try:
            coords_str = "(" + coords_str + ")"
            point_t = make_tuple(coords_str)
            if not point_t[0] in range(1, MAP_SIZE+1):
                return u"Первая координата точки {} не верна! Координаты должны быть от 1 до {} включительно"\
                    .format(coords_str, MAP_SIZE)
            if not point_t[1] in range(1, MAP_SIZE+1):
                return u"Вторая координата точки {} не верна! Координаты должны быть от 1 до {} включительно"\
                    .format(coords_str, MAP_SIZE)
            if len(point_t) != 2:
                return u"Неверный формат координат, это двумерная игра, дурни"
            return cls(point_t[0]-1, point_t[1]-1, -1, -1)
        except Exception as e:
            print "Error!! Couldn't parse a point from coordinates! - {}".format(e.message)
            return None

    @staticmethod
    def are_points_close(p1, p2):
        rx = range(p2.x - 1, p2.x + 2, 1)
        ry = range(p2.y - 1, p2.y + 2, 1)
        return p1.x in rx and p1.y in ry

    @staticmethod
    def are_skewed_oriented(p1, p2):
        rx = range(p2.x - 1, p2.x + 2, 2)
        ry = range(p2.y - 1, p2.y + 2, 2)
        return p1.x in rx and p1.y in ry

    @staticmethod
    def get_points_displacement(p1, p2):
        if p1 == p2:
            return True, Orientation.NONE
        if not Point.are_points_close(p1, p2):
            return False, Orientation.NONE
        if Point.are_skewed_oriented(p1, p2):
            return True, Orientation.SKEWED
        if p1.x in range(p2.x - 1, p2.x + 2, 2) and p1.y == p2.y:
            return True, Orientation.HORIZONTAL
        return True, Orientation.VERTICAL

    @staticmethod
    def can_add_point_to_field(field, new_point):
        for added_point in field:
            if Point.are_points_close(new_point, added_point):
                return False
        return True

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
        self.orientation = Orientation.NONE

    def __str__(self):
        points_str = u""
        for p in self.points:
            points_str += str(p)
        return u"Ship ({}) with rank = {}, orientation = {}, full_load = {}" \
            .format(points_str, self.rank, str(self.orientation), str(self.is_full()))

    def is_full(self):
        return len(self.points) == self.rank

    def check_dead(self):
        for p in self.points:
            if not p.was_hit:
                return False
        return True

    def try_attack(self, hit_point):
        for i, p in enumerate(self.points):
            if p == hit_point:
                if p.was_hit:
                    return False, SHOT_ALREADY_MADE
                p.was_hit = True
                self.points[i] = p
                if self.check_dead():
                    return True, SHOT_DRAWN_SHIP
                return True, SHOT_SHIP_WAS_HIT
        return False, None

    def try_add_point(self, point):
        if point.value == self.rank:
            if not len(self.points):
                self.points.append(point)
                return True

            for p in self.points:
                close, orientation = Point.get_points_displacement(point, p)
                if not close:
                    continue
                if orientation == Orientation.SKEWED:
                    raise MapParseException(u"Нельзя ставить точки наискосок, алё гараж!")
                if not orientation:
                    raise MapParseException(u"Что-то пошло не так, {} уже добавлена... ".format(point))
                if self.orientation and orientation != self.orientation:
                    raise MapParseException(u"Корабли не бывают изогнутыми, во чо...")
                if not self.orientation:
                    self.orientation = orientation
                if self.orientation and orientation == self.orientation:
                    if self.is_full():
                        raise MapParseException(u"Слишком много точек в корабле ранга {}".format(self.rank))
                    self.points.append(point)
                    return True
            return False
        else:
            for p in self.points:
                close, orientation = Point.get_points_displacement(point, p)
                if close:
                    raise MapParseException(u"Точка ({},{}) слишком близко к точке ({},{})".format(point.x, point.y, p.x, p.y))
            return False
