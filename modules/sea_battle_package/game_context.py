#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml

from team import *


class GameContext:
    def __init__(self, uid):
        self.uid = uid
        self.max_score = 1
        self.game_started = False
        self.this_team = None
        self.opponent = None
        self.load()

    def create_this_team(self, team_name, team_uid):
        this_team_data = {"cap_uid": team_uid,
                          "team_name": team_name,
                          "score": 0,
                          "field": [],
                          "field_of_shots": [],
                          "shots_left": 0,
                          "score_per_hit": 0,
                          "answered_questions": []}
        self.this_team = Team.create_team(this_team_data)
        return True

    def create_opponent(self, team_name, team_uid):
        if self.opponent is not None:
            return False
        op_data = {"cap_uid": team_uid,
                   "team_name": team_name,
                   "score": 0,
                   "field": [],
                   "field_of_shots": [],
                   "shots_left": 0,
                   "score_per_hit": 0,
                   "answered_questions": []}
        self.opponent = Team.create_team(op_data)
        return True

    def check_winner(self):
        t_score = self.this_team["score"]
        op_score = self.opponent["score"]
        if t_score >= self.max_score:
            return self.this_team["team_name"]
        if op_score >= self.max_score:
            return self.opponent["team_name"]
        return ""

    def load(self):
        try:
            with open("./files/seabattle_context_{}.yaml".format(self.uid), 'r') as stream:
                data = yaml.load(stream)
                self.max_score = data["max_score"]
                self.game_started = data["game_started"]
                self.this_team = Team.create_team(data["this_team"])
                self.opponent = Team.create_team(data["opponent"])
        except:
            self.max_score = 1
            self.game_started = False
            self.this_team = None
            self.opponent = None

    def save(self):
        print "Saving context for {}".format(self.uid)
        with open('./files/seabattle_context_{}.yaml'.format(self.uid), 'w') as outfile:
            data = {"max_score": self.max_score,
                    "game_started": self.game_started,
                    "this_team": Team.try_serialize(self.this_team),
                    "opponent": Team.try_serialize(self.opponent)}
            yaml.dump(data, outfile, default_flow_style=True)
