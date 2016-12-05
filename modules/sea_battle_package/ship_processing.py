#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import Orientation
from ast import literal_eval as make_tuple
from game_constants import MAP_SIZE

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
                    return False, u"Вы сюда ужо стреляли, повнимательней"
                p.was_hit = True
                self.points[i] = p
                if self.check_dead():
                    return True, u"Корабль потоплен!"
                return True, u"Ай малаца, попал! (корабль ещё жив)"
        return False, None

    @staticmethod
    def get_points_orientation(new_point, placed_point):
        range_x = range(placed_point.x - 1, placed_point.x + 2, 2)
        range_y = range(placed_point.y - 1, placed_point.y + 2, 2)
        if new_point.x in range_x and new_point.y in range_y:
            # skewed orientations ain't supported!
            return Orientation.NONE

        if new_point.x in range_x:
            return Orientation.HORIZONTAL
        if new_point.y in range_y:
            return Orientation.VERTICAL
        return Orientation.NONE

    def can_place_point(self, point, p):
        orientation = self.get_points_orientation(point, p)
        if not orientation:
            return None
        if self.orientation and self.orientation != orientation:
            return None
        return orientation

    def this_ship_point(self, point):
        if point.value != self.rank:
            return False

        belongs = len(self.points) == 0

        for p in self.points:
            orientation = self.can_place_point(point, p)
            if orientation:
                self.orientation = orientation
                belongs = True
                break
        return belongs

    def can_place_another_ship(self, point):
        for p in self.points:
            if point.x in range(p.x - 1, p.x + 2, 2) and point.y in range(p.y - 1, p.y + 2, 2):
                return False
        return True

    def add_point(self, point):
        if self.this_ship_point(point):
            if len(self.points) >= self.rank:
                return False
                # raise MapParseException(u"слишком много точек в корабле ранга {}".format(str(self.rank)))
            self.points.append(point)
            return True

        if not self.can_place_another_ship(point):
            raise MapParseException(u"корабли стоят слишком близко для ранга {}".format(self.rank))
        return False
