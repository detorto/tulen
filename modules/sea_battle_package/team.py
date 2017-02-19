#!/usr/bin/python
# -*- coding: utf-8 -*-

import ship_processing as sp
from utils import *
import random
from PIL import Image

CEIL = (67, 64)
FIELD_START = (72, 63)
SHIP_PATH = './modules/sea_battle_package/images/ship_{}d_{}.png'
EXPLOSION_PATH = './modules/sea_battle_package/images/explosion.png'
WATER_PATH = './modules/sea_battle_package/images/water.png'
FIELD_PATH = './modules/sea_battle_package/images/field{}.png'


def generate_field_of_shots():
    return ['_' for i in range(MAP_SIZE * MAP_SIZE)]


class Team:
    def __init__(self, cap_uid, team_name, bot_game, score, field, field_of_shots,
                 shots_left, score_per_hit, question_answered, answered_questions):
        self.cap_uid = cap_uid if cap_uid else ""
        self.team_name = team_name if team_name else ""
        self.bot_game = bot_game
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

    def reset_ships(self):
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
        return Team.print_fields_s(self.field, self.field_of_shots, only_shots)

    # prints either self field merged with shots made at this field
    # or only field of shots
    def print_fields_pic(self, only_shots):
        field_pic = Image.open(FIELD_PATH, 'r')

        for ship in self.ships:
            if not only_shots or (only_shots and ship.check_dead()):
                Team.place_ship(field_pic,
                                ship.rank,
                                'h' if ship.orientation == Orientation.NONE or ship.orientation == Orientation.HORIZONTAL
                                else 'v',
                                ship.get_head_point())
            for p in ship.points:
                if p.was_hit:
                    Team.place_explosion(field_pic, (p.x, p.y))
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if self.field_of_shots[j + i * MAP_SIZE] == '.':
                    Team.place_water(field_pic, (j, i))
        name = FIELD_PATH.format('_out')
        field_pic.save(name)
        return name

    @staticmethod
    def place_ship(field, size, orientation, point):
        Team.place_picture(field, SHIP_PATH.format(size, orientation), point)

    @staticmethod
    def place_explosion(field, point):
        Team.place_picture(field, EXPLOSION_PATH, point)

    @staticmethod
    def place_water(field, point):
        Team.place_picture(field, WATER_PATH, point)

    @staticmethod
    def place_picture(field, pic_name, point):
        pic = Image.open(pic_name, 'r')
        offset = (FIELD_START[0] + CEIL[0] * point[0], FIELD_START[1] + CEIL[1] * point[1])
        field.paste(pic, offset, pic)

    @staticmethod
    def print_fields_s(field, of_shots, only_shots):
        txt_field = u""

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                printed = not only_shots

                if not only_shots:
                    printed = of_shots[j + i * MAP_SIZE] == '_' and field[j + i * MAP_SIZE] != '0'
                    if printed:
                        txt_field += str(field[j + i * MAP_SIZE]) + u"\t"

                if not printed:
                    txt_field += of_shots[j + i * MAP_SIZE] + u"\t"

            txt_field += u"\n"
        return txt_field

    @staticmethod
    def generate_random_map():
        ships = {}
        field = []
        field_points = []
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                field.append(str(0))

        for rank in sp.SHIP_RANKS_DICT:
            ships[rank] = []
            for ship in range(sp.SHIP_RANKS_DICT[rank]):
                ships[rank].append(sp.Ship(rank))
            for ship in ships[rank]:
                directions = [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]
                direction = Direction.NONE
                random.shuffle(directions)

                loop_count = 0
                non_random_loop_count = 200

                while not ship.is_full():
                    loop_count += 1

                    i = random.randint(0, MAP_SIZE - 1)
                    j = random.randint(0, MAP_SIZE - 1)
                    if loop_count >= non_random_loop_count:
                        i = loop_count % MAP_SIZE
                        j = loop_count % MAP_SIZE

                        non_random_point = sp.Point(j, i, rank, False)
                        while not sp.Point.can_add_point_to_field(field_points, non_random_point):
                            if j >= MAP_SIZE:
                                j = 0
                                i += 1
                            else:
                                j += 1
                            if i >= MAP_SIZE:
                                i = MAP_SIZE - 1
                                j = MAP_SIZE - 1
                                break
                            non_random_point = sp.Point(j, i, rank, False)

                    if loop_count > non_random_loop_count + MAP_SIZE * MAP_SIZE * 3:
                        return u"Сорян, не смог загрузить карту, генератор сломался =(\nПопробуй ещё разок\n" + \
                               Team.print_fields_s(field, generate_field_of_shots(), False)

                    if rank > 1 and len(ship.points) > 0:
                        if not len(directions) and not direction:
                            ship.points = []
                            directions = [Direction.UP, Direction.DOWN, Direction.RIGHT, Direction.LEFT]
                            direction = Direction.NONE
                            random.shuffle(directions)
                            continue

                        if not direction:
                            direction = directions.pop()
                        last_point = ship.points[len(ship.points) - 1]

                        if Direction.UP == direction:
                            i = last_point.y - 1
                            j = last_point.x
                        elif Direction.DOWN == direction:
                            i = last_point.y + 1
                            j = last_point.x
                        elif Direction.RIGHT == direction:
                            i = last_point.y
                            j = last_point.x + 1
                        elif Direction.LEFT == direction:
                            i = last_point.y
                            j = last_point.x - 1

                    point = sp.Point(j, i, rank, False)
                    if not sp.Point.fits_field(point) or point in field_points or not sp.Point.can_add_point_to_field(field_points, point):
                        if len(ship.points) > 1:
                            ship.points = [ship.points[0]]
                        direction = Direction.NONE
                        continue

                    try:
                        if ship.try_add_point(point):
                            if ship.is_full():
                                for new_point in ship.points:
                                    field_points.append(new_point)
                                    field[new_point.x + new_point.y * MAP_SIZE] = str(rank)
                        else:
                            if len(ship.points) > 1:
                                ship.points = [ship.points[0]]
                            direction = Direction.NONE
                            continue
                    except Exception as e:
                        if isinstance(e, sp.MapParseException):
                            if len(ship.points) > 1:
                                ship.points = [ship.points[0]]
                            direction = Direction.NONE
                            continue
                        else:
                            raise

        return field

    def parse_fields(self, field):
        self.reset_ships()
        if field is None:
            return u"Поле пустое"
        if len(field) != MAP_SIZE * MAP_SIZE:
            msg = u"Размер поля неверен! Должно быть ровно {} точек\n".format(MAP_SIZE * MAP_SIZE)
            msg += Team.get_ship_instruction()
            return msg
        try:
            ships_filled = 0
            for i in range(MAP_SIZE):
                for j in range(MAP_SIZE):

                    was_hit = False
                    if self.field_of_shots is not None and len(self.field_of_shots) == len(field):
                        # '_' for unknown cell, '.' for missed shot, 'x' for hit ship, 'X" for drawn ship
                        was_hit = self.field_of_shots[j + i * MAP_SIZE] == 'X' or self.field_of_shots[j + i * MAP_SIZE] == 'x'

                    point = sp.Point(j, i, int(field[j + i * MAP_SIZE]), was_hit)
                    if not point.value:
                        continue

                    for rank in sp.SHIP_RANKS_DICT:
                        point_added = False
                        for ship in self.ships[rank]:
                            try:
                                if ship.try_add_point(point):
                                    point_added = True
                                    if ship.is_full():
                                        for ship_point in ship.points:
                                            self.points.append(ship_point)

                                        ships_filled += 1
                                    break
                            except Exception as e:
                                if isinstance(e, sp.MapParseException):
                                    return e.value
                                raise
                        if point_added:
                            break
                        elif point.value == rank:
                            return u"Кораблей ранга {} слишком много!".format(rank)

            if ships_filled != self.ships_count:
                msg = u"Не удалось расставить все корабли!\n" \
                      u"Проверьте ваше поле на наличие всех необходимых кораблей и точек в них\n"
                msg += Team.get_ship_instruction()
                return msg

            self.field_parsed = True
            self.field = field
            return GOOD_MAP_MSG
        except Exception as e:
            if isinstance(e, sp.MapParseException):
                return e.value
            raise

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
                "bot_game": self.bot_game,
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
                   try_get_data(data, "bot_game"),
                   try_get_data(data, "score"),
                   try_get_data(data, "field"),
                   try_get_data(data, "field_of_shots"),
                   try_get_data(data, "shots_left"),
                   try_get_data(data, "score_per_hit"),
                   try_get_data(data, "question_answered"),
                   try_get_data(data, "answered_questions"))
