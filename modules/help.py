#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import re
import random
hlp = u'''
Загляните сюда: https://vk.com/seal_in_vacuum. Если же не хотите - смотрите, что могу.

что-то.[jpg|жпг] - случайная картинка из поиска по запросу "что-то", хоть мамка ваша, хоть говно. 
Если вам внезапно прилетела капча из яндекса, напишите слово_с_капчи.[jpg|жпг]. Не забываем про .жпг, а то пойдете на то же, что искали. 

что-то.ави - случайная видеозапись из поиска 

что-то.[gif|гиф] - случайный документ из поиска 

что-то.[txt|тхт] - случайный коммент из поиска 

вики:что-то - выжимка из википедии о чем-то 

Так среди моих знакомых очень много долбоебов, поэтому поясняю на примерах:
твоя мамка.жпг
спокойной ночи.ави
война и мир.txt
вики:синхрофазатрон

Так же я умею в несколько игрушек.

ВИСИЛИЦА. 
Команда начала игры: повесьте нас
Открыть букву: буква Х
Открыть слово: слово СЛОВО

БЛЭКДЖЕК - она же очко. У каждого изначально 5000 рупий. Можно делать ставки, на людей или на тюленя. 
Команда начала игры: блэкджек
Количество денег на вашем счету: мой депозит

Комманды ставок:
ставлю на тюленя {число} - сделать ставку на тюленя, поставившие на тюленя не могут тянуть карту. 
ставлю на нас {число} - сделать ставку на людей. 

Комманды игры:
карту - взять карту из колоды 
хватит - посчитать очки, определить победителя и раздать выигрыш. 
Звучит сложно, но это проще, чем в жопу долбиться. 

Еще я умею картинки фильтровать. 
Сортани, негатни, фильтрани, рандомни - работает только с приложенными картинками
ПРИКРЕПИ КАРТИНКУ, ДОЛБОЕБ. 
Я вам не фотошоп, работаю долго и за мороженое.

А ещё появился будильник-напоминалка, но я сам не знаю как он работает. Кажется там была какая то инструкция. Кажется, такая:

инструкция по будильнику
тюлень, поставь будильник [на [дату|время] [время|дату]] [для user_id] [с текстом text]
параметр в скобках - опциональный
пример:
тюлень, поставь будильник на 23:59:59 31.12.2016 для 574627483 с текстом иметь твою мамку
тюлень, поставь будильник на 06:00 с текстом на работу пора блеать!

Внимание, баны! Отмаза "Я не знал" болье не принимается.
За спам и за поиск запрещенных материалов вы будете автоматически наказаны и помещены в черный список.

Если долго не отвечаю, то или вы мне не нравитесь или вас слишком много. 

Самое противное в вконтакте - это каптча, и я умею ее решать. Однако, это стоит некоторых денег. 
Текущий баланс на счету каптча-отгадывателя можно посмотреть коммандой "captchabalance".
Если вы хотите чтобы тюлень был всегда с вами, а не отваливался на два часа из за какого то пидора, в очередной раз решившего посмотреть на хуец,
можете задонатить любую сумму на QIWI +79166317941 или яды https://money.yandex.ru/to/41001705503465. 
Приветствую комментарий с вашем id, и тогда я придумаю как вас поблагодарить. 

Если у вас появилась замечательная идея, которую я смогу выполнить, прошу, не стесняйтесь, выкладывайте.
Пожелания и предложения, ад содом и рыбу принимаю в комментарии на стенку.

'''
commands = [u"что ты умеешь", 
		u"help",
		u"какие команды ты знаешь",
		u"какие у тебя комманды",
		u"что ты можешь",
		u"как ты работаешь",
		u"покажи что ты умеешь",
		u"тюлень, помощь",
		u"тюлень помощь"]
class Processor:

	def __init__(self, user):
		self.user = user
	def isRequest(self,message):
		for c in commands:
			if c in message:
				return True
		
	def process_message(self, message, chatid, userid):
		message_body = message["body"].lower()
		if self.isRequest(message_body):
			self.user.send_message(hlp, chatid = chatid, userid = userid)
