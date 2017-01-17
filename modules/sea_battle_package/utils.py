#!/usr/bin/python
# -*- coding: utf-8 -*-

from game_constants import *

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

class Orientation:
    def __init__(self):
        pass

    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    SKEWED = 3

class Direction:
    def __init__(self):
        pass

    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

def try_get_data(data, key):
    try:
        return data[key]
    except Exception as e:
        print e.message
        return None

def need_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        active, questioned = game_manager.session_is_active()
        # TODO: what's with questioned here?
        if active:
            return f(*args)
        else:
            # empty text cuz we don't answer without game session
            return
    return wrapper

def need_questioned_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        active, questioned = game_manager.session_is_active()
        if active:
            if not questioned:
                return u"Эта команда доступна лишь в игре с вопросами"
            return f(*args)
        else:
            # empty text cuz we don't answer without game session
            return
    return wrapper

def need_game_context(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        game_context = game_manager.game_context
        if not game_context:
            return
        return f(*args)
    return wrapper

def need_no_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return f(*args)
        active, questioned = game_manager.session_is_active()
        if not active:
            return f(*args)
        else:
            return SESSION_ALREADY_ACTIVE_MSG.format(game_manager.uid)
    return wrapper

def need_game_started(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        if game_manager.is_game_started():
            return f(*args)
        else:
            # do not return anything!!!!!
            return
    return wrapper

def need_game_not_started(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return f(*args)
        if not game_manager.is_game_started():
            return f(*args)
        else:
            return IMPOSSIBLE_DURING_GAME
    return wrapper

def need_registration(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        if game_manager.get_team_name() and game_manager.game_context.this_team:
            return f(*args)
        else:
            return NOT_REGISTERED_YET_MSG
    return wrapper

def can_register_team(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        message = args[1]
        # from forth word
        team_name = "".join(message.split()[3:]).strip()

        if not team_name:
            return TEAM_NAME_IS_EMPTY_MSG

        if team_name in game_manager.teams:
            return ALREADY_REGISTERED_MSG.format(team_name)

        if game_manager.get_team_name():
            return ALREADY_CAPTAIN_MSG

        return f(*args)
    return wrapper

def need_valid_map(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        gc = game_manager.game_context
        if gc.this_team and gc.this_team.field_parsed:
            return f(*args)
        else:
            return NO_MAP_YET_MSG
    return wrapper

def need_opponent_set(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        game_context = game_manager.game_context
        if game_context.opponent:
            return f(*args)
        else:
            return NO_OPPONENT_SET_MSG
    return wrapper

def need_no_opponent_set(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        game_context = game_manager.game_context
        if not game_context.opponent and not game_context.op_team_name:
            return f(*args)
        else:
            return OPPONENT_IS_ALREADY_SET_MSG.format(game_context.op_team_name)
    return wrapper

def need_question_answered(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager:
            return
        active, questioned = game_manager.session_is_active()
        if not questioned:
            return f(*args)
        gc = game_manager.game_context
        if gc.this_team.question_answered:
            return f(*args)
        else:
            return u"Для выстрела необходимо ответить на вопрос!"
    return wrapper
