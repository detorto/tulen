#!/usr/bin/python
# -*- coding: utf-8 -*-

from game_constants import *

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

def try_get_data(data, key):
    try:
        return data[key]
    except Exception as e:
        print e.message
        return None

def need_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if game_manager.session_is_active():
            return f(*args)
        else:
            # empty text cuz we don't answer without game session
            return
    return wrapper

def need_no_game_session(f):
    def wrapper(*args):
        game_manager = args[0]
        if not game_manager.session_is_active():
            return f(*args)
        else:
            return SESSION_ALREADY_ACTIVE_MSG.format(game_manager.uid)
    return wrapper

def need_game_started(f):
    def wrapper(*args):
        game_manager = args[0]
        game_context = game_manager.game_context
        if game_context.game_started:
            return f(*args)
        else:
            return
    return wrapper

def need_game_not_started(f):
    def wrapper(*args):
        game_manager = args[0]
        game_context = game_manager.game_context
        if not game_context.game_started:
            return f(*args)
        else:
            return IMPOSSIBLE_DURING_GAME
    return wrapper

def need_registration(f):
    def wrapper(*args):
        game_manager = args[0]
        if game_manager.is_team_registered():
            return f(*args)
        else:
            return NOT_REGISTERED_YET_MSG
    return wrapper

def need_not_registered(f):
    def wrapper(*args):
        game_manager = args[0]
        message = args[1]
        team_name = "".join(message.split()[3:]).strip()

        if not team_name:
            return TEAM_NAME_IS_EMPTY_MSG

        if game_manager.game_context.this_team or team_name in game_manager.teams:
            return ALREADY_REGISTERED_MSG.format(team_name)

        for t_name in game_manager.teams.keys():
            if game_manager.teams[t_name]["team_uid"] == game_manager.uid:
                return ALREADY_CAPTAIN_MSG

        return f(*args)
    return wrapper

def need_valid_map(f):
    def wrapper(*args):
        game_manager = args[0]
        game_context = game_manager.game_context
        if game_context.this_team and game_context.this_team.field_parsed:
            return f(*args)
        else:
            return NO_MAP_YET_MSG
    return wrapper

def need_opponent_set(f):
    def wrapper(*args):
        game_manager = args[0]
        game_context = game_manager.game_context
        if game_context.opponent is None:
            return f(*args)
        else:
            return NO_OPPONENT_SET_MSG
    return wrapper

def need_no_opponent_set(f):
    def wrapper(*args):
        game_manager = args[0]
        game_context = game_manager.game_context
        if not game_context.opponent:
            return f(*args)
        else:
            return OPPONENT_IS_ALREADY_SET_MSG.format(try_get_data(game_context.opponent, "team_name"))
    return wrapper

