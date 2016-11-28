#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

from team import *


class GameContext:
    def __init__(self, uid, max_score, team_name="", op_team_name=""):
        self.uid = uid
        self.max_score = max_score
        self.this_team = None
        self.this_team_name = team_name
        self.opponent = None
        self.op_team_name = op_team_name
        self.load()

    def is_game_started(self):
        return self.this_team is not None and self.opponent is not None

    @staticmethod
    def create_team(team_name, team_uid):
        team_data = {"cap_uid": team_uid,
                     "team_name": team_name,
                     "score": 0,
                     "field": [],
                     "field_of_shots": [],
                     "shots_left": 0,
                     "score_per_hit": 0,
                     "question_answered": False,
                     "answered_questions": []}
        return Team.create_team(team_data)

    def check_winner(self):
        t_score = self.this_team["score"]
        op_score = self.opponent["score"]
        if t_score >= self.max_score:
            return self.this_team
        if op_score >= self.max_score:
            return self.op_team_name
        return ""

    @staticmethod
    def load_team_data(team_name):
        try:
            if not team_name:
                return None
            with open("./files/seabattle_team_data_{}.yaml".format(team_name), 'r') as stream:
                data = yaml.load(stream)
                return Team.create_team(data["this_team"])
        except:
            return None

    @staticmethod
    def save_team_data(team):
        team_name = ""
        try:
            if not team:
                return False
            team_name = team.team_name
            with open("./files/seabattle_team_data_{}.yaml".format(team_name), 'w') as outfile:
                data = {"this_team": Team.try_serialize(team)}
                yaml.dump(data, outfile, default_flow_style=True)
                return True
        except Exception as e:
            print "Exception occurred while saving team data for team {} - {}".format(team_name, e.message)
            return False

    def load(self):
        self.this_team = GameContext.load_team_data(self.this_team_name)
        self.opponent = GameContext.load_team_data(self.op_team_name)

    def save(self):
        GameContext.save_team_data(self.this_team)
        GameContext.save(self.opponent)
