#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

from team import *


class GameContext:
    def __init__(self, uid, max_score, directory, bot_game, team_name="", this_cap_uid="", op_team_name="", op_cap_uid=""):
        self.uid = uid
        self.max_score = max_score
        self.this_team = None
        self.this_team_name = team_name
        self.this_cap_uid = this_cap_uid
        self.opponent = None
        self.op_team_name = op_team_name
        self.op_cap_uid = op_cap_uid
        self.bot_game = bot_game
        self.directory = directory
        self.load()

    @staticmethod
    def create_team(team_name, team_uid, bot_game=False):
        team_data = {"cap_uid": team_uid,
                     "team_name": team_name,
                     "bot_game": bot_game,
                     "score": 0,
                     "field": [],
                     "field_of_shots": [],
                     "shots_left": 0,
                     "score_per_hit": 0,
                     "question_answered": False,
                     "answered_questions": []}
        return Team.create_team(team_data)

    def check_winner(self):
        if not self.this_team or not self.opponent:
            return None
        t_score = self.this_team.score
        op_score = self.opponent.score
        if t_score >= self.max_score:
            return self.this_team_name
        if op_score >= self.max_score:
            return self.op_team_name
        if self.this_team.get_alive_ships_count() == 0:
            return self.op_team_name
        elif self.opponent.get_alive_ships_count() == 0:
            return self.this_team_name
        return None

    @staticmethod
    def load_team_data(team_cap_uid, directory):
        try:
            if not team_cap_uid:
                return None, None
            with open(directory + "/seabattle_team_data_{}.yaml".format(team_cap_uid), 'r') as stream:
                data = yaml.load(stream)
                return Team.create_team(try_get_data(data, "this_team")), Team.create_team(try_get_data(data, "opponent"))
        except Exception as e:
            print "Exception occurred while loading team data for captain {} - {}".format(team_cap_uid, e.message)
            return None, None

    @staticmethod
    def save_team_data(team, opponent, directory):
        try:
            if not team:
                return False
            cap_uid = team.cap_uid
            with open(directory + "/seabattle_team_data_{}.yaml".format(cap_uid), 'w') as outfile:
                data = {"this_team": Team.try_serialize(team), "opponent": Team.try_serialize(opponent)}
                yaml.dump(data, outfile, default_flow_style=True)
                return True
        except Exception as e:
            print "Exception occurred while saving team data - {}".format(e.message)
            return False

    def load(self):
        self.this_team, self.opponent = GameContext.load_team_data(self.this_cap_uid, self.directory)
        if self.this_team:
            self.this_team.parse_fields(self.this_team.field)
            if self.opponent:
                self.opponent.parse_fields(self.opponent.field)

    def save(self):
        GameContext.save_team_data(self.this_team, self.opponent, self.directory)
        if not self.bot_game:
            GameContext.save_team_data(self.opponent, self.this_team, self.directory)
