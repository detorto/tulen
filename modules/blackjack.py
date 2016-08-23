#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import requests
import io
import copy
#from utils import *

def load_json(filename):
        try:
                data = json.load(open(filename))
        except:
                return None

        return data

import random


greetings = [   u"Охуеть, ну вообще прям, молодцы!",
                u"Ох ты ебаный ты нахуй, да это же победа!",
                u"Вау, вот это да, поздравляю!",
                u"Таки вы прямо филологи, пагни",
                u"Как боги",
                u"Я БЛЯ ДОЛГА ПИЗДЕТЬ НЕ СТАНУ!\nХОЧЕШ ХУЙ ИЗ ШТАНОВ ДОСТАНУ?\nХОЧЕШ ВСЁ РАЗЪЕБУ ВЗАМЕС?\nПАЗДРАВЛЯЮ ТЕБЯ БАЛБЕС!",
                u"Ладно, ладно, вы победили"]

looses = [u"Ну все, кровь кишки распидорасило",
          u"Гроб гроб кладбище, пидор, смерть мерзкая",
          u"Кажется вы слегка обьебались",
          u"Подставляй туза, маня",
          u"Лохи",
          u"И ТУТ СУКА ВЗРЫВ НАХУЙ КИШКИ В СТЕНУ БЛЯДЬ МОЗГИ ГОВНО РАСЧЛЕНЕНКА",
          u"Слышиш ты дитя отродия антихриста,Угомонись и не осерай людей,блин а то можем только ты и я встретиться и таких пиздюлей выхватишь,я таких как ты в мире не видела,урод вышего коления!Опустись и посмотри в зеркало,а за тем с испугу ударься головой об стену!Если я живу в Украине это ничо не значит,я вообщето русская и пизды дам ебать сам себя будешь!!!!Свернись в клубочик и утихни!",
        ]

cards = [   {u"2":u"пикей"},{u"2":u"червей"},{u"2":u"бубей"},{u"2":u"крестей"},
            {u"3":u"пикей"},{u"3":u"червей"},{u"3":u"бубей"},{u"3":u"крестей"},
            {u"4":u"пикей"},{u"4":u"червей"},{u"4":u"бубей"},{u"4":u"крестей"},
            {u"5":u"пикей"},{u"5":u"червей"},{u"5":u"бубей"},{u"5":u"крестей"},
            {u"6":u"пикей"},{u"6":u"червей"},{u"6":u"бубей"},{u"6":u"крестей"},
            {u"7":u"пикей"},{u"7":u"червей"},{u"7":u"бубей"},{u"7":u"крестей"},
            {u"8":u"пикей"},{u"8":u"червей"},{u"8":u"бубей"},{u"8":u"крестей"},
            {u"9":u"пикей"},{u"9":u"червей"},{u"9":u"бубей"},{u"9":u"крестей"},
            {u"10":u"пикей"},{u"10":u"червей"},{u"10":u"бубей"},{u"10":u"крестей"},
            {u"валет":u"пикей"},{u"валет":u"червей"},{u"валет":u"бубей"},{u"валет":u"крестей"},
            {u"дама":u"пикей"},{u"дама":u"червей"},{u"дама":u"бубей"},{u"дама":u"крестей"},
            {u"король":u"пикей"},{u"король":u"червей"},{u"король":u"бубей"},{u"король":u"крестей"},
            {u"туз":u"пикей"},{u"туз":u"червей"},{u"туз":u"бубей"},{u"туз":u"крестей"}]


def card_cost(card, scores):
    num = card.items()[0][0]
    print num
    if num not in [u"король",u"валет",u"дама",u"туз"]:
        return int(num)

    if num in [u"король",u"валет",u"дама"]:
        return 10
    if num == u"туз":
        if scores > 21:
            return 1
        else:
            return 11

def shuffle_cards():
    import copy
    #print cards
    cc = copy.copy(cards)
    random.shuffle(cc)
    return cc

PATH = "./files/blackjack_{}.context"
CONFIG_FILE = "conf.yaml"

import yaml
class Processor:
        def __init__(self, vkuser):
                self.config = yaml.load(open(vkuser.module_file("blackjack", CONFIG_FILE)))
                self.user = vkuser
                self.benderstack = []
                self.userstack = []
                self.game_context = load_json(PATH.format(0))
                if not self.game_context:
                        self.new_game_context()
                else:
                    self.stack = self.game_context["stack"]
                    self.userstack = self.game_context["user"]
                    self.benderstack = self.game_context["bender"]

        
        def generate_stack(self):
            #print "Gen stack"
            self.stack = shuffle_cards()
            #print self.stack

        def take_cards(self):
            if len(self.stack) > 0:
                card = self.stack.pop(0)
                self.userstack.append(card)
            if len(self.stack) > 0 and self.get_bender_scores()<20:
                card = self.stack.pop(0)
                self.benderstack.append(card)

            
        def new_game_context(self):
            print "New context"
            self.generate_stack()
            self.userstack = []
            self.benderstack = []
            self.take_cards()
            self.take_cards()
            if not self.game_context:
                print "New game context"
                self.game_context = {"gamers" : {}, "bender_bets":[], "user_bets":[],
                            "stack" : self.stack, "bender":self.benderstack, "user":self.userstack,"session_started":True}
            else:
                print "New stack"
                self.game_context["stack"] = self.stack
                self.game_context["bender"] = self.benderstack
                self.game_context["user"] = self.userstack
                self.game_context["session_started"] = True
                self.payback_users();
                self.game_context["bender_bets"] = []
                self.game_context["user_bets"] = []


        def gen_win_or_loose_text(self, win):
            tbot = self.total_on_bot()
            tuser = self.total_on_user()
            ratio = 0
            if tuser > 0:
                ratio = tbot/tuser
            text = u"Ставки: на тюленя: {}, на нас: {}\n".format(tbot,tuser)
            
            text = u"\nу тюленя - {} очков".format(self.get_bender_scores())
            text += u"\nу вас - {} очков".format(self.get_user_scores())

            self.refund_users(win)
            self.game_context["bender_bets"] = []
            self.game_context["user_bets"] = []

            if win:
                text += u"\n Победили мы!"
            else:
                text += u"\n Победил Тюлень = ("
            return text

        def generate_message(self, finish=False):
            
            text = u""
            if not finish:
                tbot = self.total_on_bot()
                tuser = self.total_on_user()
                ratio = 0
                if tuser > 0:
                    ratio = tbot/tuser
                text += u"Ставки: на тюленя: {}, на нас: {}\n".format(tbot,tuser)
                text += u"{} карт(ы) у тюленя\n".format(len(self.benderstack))
                text += u"{} карт(ы) у вас: ".format(len(self.userstack))

                userscores = self.get_user_scores()
                cardtext = []
                for card in self.userstack:
                    ct = card.items()[0][0]
                    ct += u" "+card.items()[0][1]#+u"# (стоит: {})".format(card_cost(card,userscores))
                    cardtext.append(ct)
                text += ", ".join(cardtext)
                text += "\n"
                text+=u"Очков: {}".format(userscores)

            if self.get_user_scores() >= 21:
                finish = True;

            if finish:
                self.game_context["session_started"] = False
                if self.get_user_scores() == 21:
                    return text+self.gen_win_or_loose_text(True)

                if self.get_user_scores() > 21:
                    return text+self.gen_win_or_loose_text(False)
                if self.get_bender_scores() > 21:
                    return text+self.gen_win_or_loose_text(True)
                if self.get_user_scores() > self.get_bender_scores():
                    return text+self.gen_win_or_loose_text(True)
                else:
                    return self.gen_win_or_loose_text(False)

            return text
        def get_scores(self,stack):
            cost = 0;
            for card in stack:
                cost+=card_cost(card,cost)
            res = 0
            for card in stack:
                res += card_cost(card,cost)
            return res

        def get_user_scores(self):
            return self.get_scores(self.userstack)
        def get_bender_scores(self):
            return self.get_scores(self.benderstack)


        def save_context(self):
                #print "Saving context"
                #print self.game_context
                with io.open(PATH.format(0), 'w', encoding='utf-8') as f:
                        f.write(unicode(json.dumps(self.game_context, ensure_ascii=False,indent=4, separators=(',', ': '))))

        def process_bet_on_user(self,uid, bet):
            
            if not self.has_money(uid):
                self.add_money(1000,uid)

            if self.get_money(uid) < bet:
                bet = self.get_money(uid)
            if bet == 0:
                return u"Да вы банкрот, батенька, пиздуйте из казино."

            self.bet_on_user(bet, uid)
            self.decrease_money(bet, uid)
            return u"Ставка в размере {} рупий на нас принята".format(bet)

        def process_bet_on_bot(self,uid, bet):
            if not self.has_money(uid):
                self.add_money(1000,uid)

            if self.get_money(uid) < bet:
                bet = self.get_money(uid)
            if bet == 0:
                return u"Да вы банкрот, батенька, пиздуйте из казино."

            self.bet_on_bot(bet, uid)
            self.decrease_money(bet, uid)
            return u"Ставка в размере {} рупий на бота принята".format(bet)

        def has_money(self, uid):
            if uid in self.game_context["gamers"].keys():
                return True
            else:
                return False

        def get_money(self, uid):
            return self.game_context["gamers"][uid]["money"]
        
        def add_money(self, num, uid):
            print "Adding money {} to  {}".format(num,uid)
            if uid in self.game_context["gamers"].keys():
                self.game_context["gamers"][uid]["money"]+=num
            else:
                self.game_context["gamers"][uid] = {"money":num}


        def decrease_money(self, num, uid):
            self.game_context["gamers"][uid]["money"]-=num

        def bet_on_bot(self, num, uid):
            self.game_context["bender_bets"].append((uid,num))
        
        def bet_on_user(self, num, uid):
            self.game_context["user_bets"].append((uid,num))

        def get_deposit(self, uid):

            if not self.has_money(uid):
                self.add_money(1000,uid)

            return u"У вас на счету {}, дорогуша".format(self.get_money(uid))

        def total_on_bot(self):
            num = 0
            for bet in self.game_context["bender_bets"]:
                num += bet[1]

            return num

        def total_on_user(self):
            num = 0
            for bet in self.game_context["user_bets"]:
                num += bet[1]

            return num
        def payback_users(self):
            for it in self.game_context["bender_bets"]:
                self.add_money(it[1],it[0])

            for it in self.game_context["user_bets"]:
                self.add_money(it[1],it[0])
        def refund_users(self, we_win):
            print "refunding"
            utotal = self.total_on_user()
            btotal = self.total_on_bot()
            k = 0;
            if we_win:
                if utotal == 0:
                    k = 0
                else:
                    k = float(btotal)/float(utotal)

                print "Ration is ", k

                for it in self.game_context["user_bets"]:
                    self.add_money(it[1]+it[1]*k,it[0])
            else:
                if btotal == 0:
                    k = 0
                else:
                    k = float(utotal)/float(btotal)
                print "Ration is ", k
                
                for it in self.game_context["bender_bets"]:
                    self.add_money(it[1]+it[1]*k,it[0])

            a = len(self.game_context["bender_bets"])+len(self.game_context["user_bets"])
            if a == 1:
                for it in self.game_context["user_bets"]:
                    self.add_money(it[1]*0.25,it[0])
                for it in self.game_context["bender_bets"]:
                    self.add_money(it[1]*0.25,it[0])


            


        def process_message(self, message, chatid, userid):

                        message_body = message["body"].lower().strip()

                        if message_body.startswith(self.config["react_on"]):
                                self.new_game_context()
                                text = self.generate_message()
                                self.save_context()
                                self.user.send_message(text = text, chatid=chatid, userid=userid)
                                return
                        
                       
                        if message_body.startswith(u"мой депозит"):
                            text = self.get_deposit(message["user_id"])
                            self.save_context()
                            self.user.send_message(text, chatid=chatid, userid=userid)        
                        

                        if not self.game_context["session_started"]:
                                return

                        if message_body.startswith(u"карту"):
                            for i in self.game_context["bender_bets"]:
                                if message["user_id"] == i[0]:
                                    self.user.send_message(u"Вы поставили на тюленя, не мешайте игре", chatid=chatid, userid=userid)                                                
                                    return

                            self.take_cards()
                            text = self.generate_message()
                            self.save_context()
                            self.user.send_message(text = text, chatid=chatid, userid=userid)
                            return

                        if message_body.startswith(u"хватит"):
                            for i in self.game_context["bender_bets"]:
                                if message["user_id"] == i[0]:
                                    self.user.send_message(u"Вы поставили на тюленя, не мешайте игре", chatid=chatid, userid=userid)                                                
                                    return

                            text = self.generate_message(finish=True)
                            self.save_context()

                            self.user.send_message(text, chatid=chatid, userid=userid)        
                            return

                        if message_body.startswith(u"ставлю на бота"):
                            bet = None
                            try:
                                bet = int(message_body[len(u"ставлю на бота"):])
                            except:
                                return    
                            if not bet:
                                return
                            print "Bet on bot ", bet
                            text = self.process_bet_on_bot(message["user_id"],bet)
                            self.save_context()
                            self.user.send_message(text, chatid=chatid, userid=userid)        

                        if message_body.startswith(u"ставлю на тюленя"):
                            bet = None
                            try:
                                bet = int(message_body[len(u"ставлю на тюленя"):])
                            except:
                                return    
                            if not bet:
                                return
                            print "Bet on bot ", bet
                            text = self.process_bet_on_bot(message["user_id"],bet)
                            self.save_context()
                            self.user.send_message(text, chatid=chatid, userid=userid)        
                        
                        
                        if message_body.startswith(u"ставлю на нас"):
                            bet = None
                            try:
                                bet = int(message_body[len(u"ставлю на нас"):])
                            except:
                                return
                            print "Bet on user: ", bet
                            if not bet:
                                return    
                            text = self.process_bet_on_user(message["user_id"],bet)
                            self.save_context()
                            self.user.send_message(text, chatid=chatid, userid=userid)        
                        return

if __name__ == '__main__':
        class user:
                def send_message(self,text,chatid,userid):
                        print text
                user = "asdasd"
        p = Processor({u"react_on":u"блекджек"}, user())

        while True:
                msg = raw_input(">> ")
                import sys
                p.process_message({"user_id":sys.argv[1],"body":msg.decode("utf-8")},0,0)

