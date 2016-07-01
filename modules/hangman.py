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


img0 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u"       ║   █", 
                u"       ║   ", 
                u"       ║   ", 
                u"       ║   ",
                u"─────╨─────" ]


img1 = [u" ╔═══╦══╗", 
                u" ║    ║   █",
                u" ▒    ║   █", 
                u"       ║   ", 
                u"       ║   ", 
                u"       ║   ",
                u"─────╨─────" ]


img2 = [u" ╔═══╦══╗", 
                u" ║    ║   █",
                u" ▒    ║   █", 
                u" ▐    ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]

img3 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐     ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]
img4 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u"       ║   ",
                u"─────╨─────" ]
img5 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u" /      ║   ",
                u"─────╨─────" ]
img6 = [u" ╔═══╦══╗", 
                u" ║    ║    █",
                u" ▒    ║    █", 
                u"/▐\    ║   ", 
                u" ▐    ║   ", 
                u" / \    ║   ",
                u"─────╨─────" ]

images = [img0, img1, img2, img3, img4, img5, img6]

import random

secret_words = [ u"пукан", 
                u"рачьё",
                u"школьник",
                u"фал",
                u"штефан",
                u"белова",
                u"торт",
                u"дота",
                u"курва",
                u"проигрыш",
                u"сепульки",
                u"коврижка",
                u"пиздарики",
                u"когда же вы угомонитесь",
		u"гарпинченко",
		u"крокодилзалупасыр",
		u"хуйпиздаджигурда",
		u"жопень",
		u"дикаприо",
		u"пидары",
		u"анальная кара вас настигнет",
		u"говно",
		u"гравитифоллз"
		u"оскар",
		u"гегельмудак",
		u"беспалова",
		u"диплодок",
		u"манда",
		u"азаза",
		u"мамкуибал",
		u"азазамамкуибал"]


def load_random_word():
        lines = open("./files/dict_utf8.txt").readlines()
        #lines = [u"абырвалг\r\n",u"синхрофазатрон\r\n",u"пхукет\r\n",u"пипипик\r\n",u"дрылл\r\n"]
        lines = [ l.decode("utf-8")[:-2] for l in lines ]

        a = lines
        if random.randint(0,100) < 20:
            a = secret_words

        return a[random.randint(0,len(a)-1)];

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
	u"А я люблю когда понос. Это же приятно. Я всегда радуюсь когда у меня понос. Дристня так прикольно вылетает. Особенно я люблю когда она выходит под напором, тогда она рекашетит от днища унитаза и ударяет мне в зад, это так прохладно и приятно, особенно меня веселит, когда некоторые капли вылетают наружу и падают на пол. Тогда я могу уверенно сказать что покакал на славу и день не прошёл зря.",
	u"Cамое стршное, что можно представить — это НЕВИДИМОЕ ГОВНО. Если оно появится, то миру конец!!! Подумайте сами… Идёшь по улице — чисто, наступил в невидимое говно, пришёл на работу и воняешь, а его не видно и не понятно откуда пахнет. Все думают, что вот млядь обосрался ты. А ты стремаешься, озираешься, подошвы рассматриваешь, ощупываешь себя — вот и руки уже в невидимом говне. Так весь перемажешься, и под ногтями застрянет, и всю клавиатуру перемажешь, и мышку. Всё в говне, воняет, а чисто и аккуратно. Из-за такого дела происходит срыв работы. Едешь домой, а там уже все поручни в метро в говне (не только же ты наступил в невидимое говно), вонь страшная, некоторые уже блюют… Не пожрать — руки в говне, мыть без толку — краны в говне и ручки дверные… Ужас и кошмар!!! Крах и апокалипсис!!!",
	u"""ВСЯ СОВА В ГОВНЕ!
ВСЁ ГОВНО В СОВЕ!
ОТМЫТЬ СОВУ!
Георгий Жарков ебал хрустальной совой 19-летнего психически больного юношу Александра.
ВСЯ СОВА В ГОВНЕ!
ВСЁ ГОВНО В СОВЕ!
ОТМЫТЬ СОВУ!
Жертва домогательств Жаркова-Пуха — быдло.
ВСЯ СОВА В ГОВНЕ!
ВСЁ ГОВНО В СОВЕ!
ОТМЫТЬ СОВУ!
Жарков хорошему человеку хрустальную сову в жопу не засунет.
ВСЯ СОВА В ГОВНЕ!
ВСЁ ГОВНО В СОВЕ!
ОТМЫТЬ СОВУ!
19-летний юноша считал себя Александром Македонским. За это и поплатился аналом.
ВСЯ СОВА В ГОВНЕ!
ВСЁ ГОВНО В СОВЕ!
ОТМЫТЬ СОВУ!""",
        ]

class Processor:
        def __init__(self, config, user):
                self.config = config
                self.user = user

                self.game_context = load_json("./files/hangman_{}.context".format(self.user.user))
                if not self.game_context:
                        self.game_context = {"word":load_random_word(), "opened": [], "errors":[], "session_started":False }

        def save_context(self, cid):
                with io.open("./files/hangman_{}.context".format(cid), 'w', encoding='utf-8') as f:
                        f.write(unicode(json.dumps(self.game_context, ensure_ascii=False,indent=4, separators=(',', ': '))))
	def load_context(self, cid):
		self.game_context = load_json("./files/hangman_{}.context".format(cid))
                if not self.game_context: 
                        self.game_context = {"word":load_random_word(), "opened": [], "errors":[], "session_started":False }

        def generate_message(self):
                print self.game_context
                print self.game_context["word"]
                imgp = len(self.game_context["errors"])

                if imgp >= len(images):
                        imgp = len(images)-1

                img = copy.copy(images[imgp])

                img[3] += u" Слово: "

                for l in self.game_context["word"]:
                        if l in self.game_context["opened"]:
                                img[3] += l + u" "
                        else:
                                img[3] += u"_ "


                img[3] += u"("+str(len(self.game_context["word"]))+u")"
                img[4] += u" Ошибки: "
                img[4] += u", ".join(self.game_context["errors"])


                if self.is_end():

                    if self.is_win():
                        pp = random.randint(0, len(greetings) - 1)
                        img[6] +=  u"\n" + greetings[pp]
                    else:
                        img[6] +=  u"\n" +  looses[random.randint(0,len(looses)-1)] + u"\nСлово: " + self.game_context["word"]

                return "\n".join(img).replace(' ',"&#8194;");



        def process_message(self, message, chatid, userid):
			self.load_context(chatid or userid)
                        message_body = message["body"].lower().strip()

                        if message_body.startswith(self.config["react_on"]):
                                self.game_context = {"word" : load_random_word(), "opened": [], "errors":[], "session_started" : True }
                                self.save_context(chatid or userid)
                            
                                self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)
                                return

                        if not self.game_context["session_started"]:
                                return

                        if message_body.startswith(u"слово"):

                                word = message_body[len(u"слово"):].strip();

                                self.open_word(word)
                                self.save_context(chatid or userid)

                                self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)
                                
                                return

                        if not message_body.startswith(u"буква"):
                                return

                        letter = message_body[len(u"буква"):].strip()[0]

                        self.open_letter(letter)
                        self.save_context(chatid or userid)
                        self.user.send_message(text = self.generate_message(), chatid=chatid, userid=userid)

                        return

        def open_word(self,word):
        
            if word == self.game_context["word"]:

                self.game_context["opened"].extend([w for w in word])
                self.game_context["opened"] = list(set(self.game_context["opened"]))
                if self.is_end():
                    self.game_context["session_started"] = False;
            else:
                self.game_context["errors"].extend([w for w in word])

            
        def open_letter(self,letter):
            if letter in self.game_context["word"]:
                self.game_context["opened"].append(letter)
            else:
                self.game_context["errors"].append(letter)
                self.game_context["errors"] = list(set(self.game_context["errors"]))

            if self.is_end():
                    self.game_context["session_started"] = False;
                

        def is_end(self):
            if len(self.game_context["errors"]) >= 6:
                return True
            
            return self.is_win()

            
        def is_win(self):
            for l in self.game_context["word"]:
                if l not in self.game_context["opened"]:
                    return False
            return True;


if __name__ == '__main__':
        class user:
                def send_message(self,text,chatid,userid):
                        print text
                user = "asdasd"
        p = Processor({u"react_on":u"повесьте нас"}, user())

        while True:
                msg = raw_input(">> ")
                p.process_message({"body":msg.decode("utf-8")},0,0)

