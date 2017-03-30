#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import io
import yaml
from datetime import datetime, timedelta
import random
from threading import Timer
import logging

# logger = logging.getLogger(__name__)
logger = logging.getLogger("tulen")

CONFIG_FILE = "conf.yaml"


def datetime_to_json(x):
    if isinstance(x, datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%S")
    return x


def datetime_from_json(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except:
            pass
    return json_dict


def load_json(filename):
    try:
        data = json.load(open(filename), object_hook=datetime_from_json)
    except:
        return None

    return data


timeCommand = u" на "
userCommand = u" для "
textCommand = u" с текстом "

timeFormats = [{"format": "%d.%m.%y %H:%M:%S", "replace": None},
               {"format": "%d.%m.%y %H:%M", "replace": None},
               {"format": "%d.%m.%y %H", "replace": None},
               {"format": "%d.%m %H:%M:%S", "replace": ["y"]},
               {"format": "%d.%m %H:%M", "replace": ["y"]},
               {"format": "%d.%m %H", "replace": ["y"]},
               {"format": "%d %H:%M:%S", "replace": ["y", "m"]},
               {"format": "%d %H:%M", "replace": ["y", "m"]},
               {"format": "%d %H", "replace": ["y", "m"]},
               {"format": "%H:%M:%S", "replace": ["y", "m", "d"]},
               {"format": "%H:%M", "replace": ["y", "m", "d"]},
               {"format": "%H", "replace": ["y", "m", "d"]},
               {"format": "%H:%M:%S %d.%m.%y", "replace": None},
               {"format": "%H:%M %d.%m.%y", "replace": None},
               {"format": "%H %d.%m.%y", "replace": None},
               {"format": "%H:%M:%S %d.%m", "replace": ["y"]},
               {"format": "%H:%M %d.%m", "replace": ["y"]},
               {"format": "%H %d.%m", "replace": ["y"]},
               {"format": "%H:%M:%S %d", "replace": ["y", "m"]},
               {"format": "%H:%M %d", "replace": ["y", "m"]},
               {"format": "%H %d", "replace": ["y", "m"]}]


# тюлень, поставь будильник [на [dd[.mm][.yy]] [hh[:mm][:ss]]] [для userId] [с текстом "text"]

class Processor:
    def __init__(self, vkuser):
        self.config = yaml.load(open(vkuser.module_file("alarm", CONFIG_FILE)))
        self.user = vkuser
        self.alarms = {}

    def process_message(self, message, chatid, userid):
        try:
            message_body = message["body"].lower().strip()
            try:
                self.load_alarms(chatid or userid)
            except Exception as e:
                logger.warning("Alarm module (user_id:{}): Failed to load alarms"
                               .format(userid))

            if message_body.startswith(self.config["react_on"]):
                try:
                    self.parse_message(message_body, chatid, userid)
                except Exception as e:
                    logger.error(
                        "Alarm module (user_id:{}): Exception occurred while parsing message - {}"
                            .format(userid, e.message))
                    self.user.send_message(text=random.choice(self.config["responds_on_exception"]),
                                           chatid=chatid, userid=userid)
            elif message_body.startswith(self.config["help_request"]):
                msg = u"инструкция по будильнику:\n" \
                      u"тюлень, поставь будильник [на [дату|время] [время|дату]] [для user_id|domain] [с текстом text]\n" \
                      u"з.ы. параметр в скобках - опциональный\n" \
                      u"з.з.ы 'user_id' - число XXX в урле вида https://vk.com/idXXX. Например, в урле вида https://vk.com/id402916056 user_id = 402916056\n" \
                      u"Иначе, если в урле текст после слэша вместо idXXX, например, https://vk.com/jiisus, то используется domain = jiisus вместо user_id."
                self.user.send_message(text=msg, chatid=chatid, userid=userid)
        except:
            return

    def save_alarms(self, chat_id):
        with io.open("./files/alarms_{}.context".format(chat_id), 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(self.alarms, ensure_ascii=False, indent=4, separators=(',', ': '),
                                       default=datetime_to_json)))

    def load_alarms(self, chat_id):
        self.alarms = load_json("./files/alarms_{}.context".format(chat_id))
        if not self.alarms:
            self.alarms = {}
        else:
            for alarm_id in self.alarms.keys():
                if self.alarms[alarm_id]["time"] < datetime.now():
                    del self.alarms[alarm_id]
                else:
                    self.set_alarm_clock(alarm_id)

    @staticmethod
    def compose_message_on_timeout(time, message):
        return u"Alarm! Achtung! Внимание! На {} у вас назначено: {}" \
            .format(time.strftime("%d.%m.%Y %H:%M:%S"), message)

    def timeout(self, chat_id, user_id, time, message):
        self.user.send_message(text=self.compose_message_on_timeout(time, message),
                               chatid=chat_id, userid=user_id)

    def set_alarm_clock(self, alarm_id):
        chat_id = self.alarms[alarm_id]["chat_id"]
        user_id = self.alarms[alarm_id]["user_id"]
        time = self.alarms[alarm_id]["time"]
        message = self.alarms[alarm_id]["message"]
        try:
            t = Timer((time - datetime.now()).total_seconds(), self.timeout,
                      [chat_id, user_id, time, message])
            t.start()
        except Exception as e:
            logger.error(
                "Alarm module (user_id:{}): Exception occurred while setting alarm clock message - {}"
                    .format(user_id, e.message))
            raise

    def parse_message(self, original_message, chat_id, user_id):
        command = original_message.split(self.config["react_on"])[1]
        message = u"Alarm!"
        receiver_id = user_id
        time = None

        if command.find(timeCommand) >= 0:
            ending = len(command)
            if command.find(userCommand, command.index(timeCommand) + len(timeCommand)) >= 0:
                ending = command.index(userCommand)
            elif command.find(textCommand, command.index(timeCommand) + len(timeCommand)) >= 0:
                ending = command.index(textCommand)

            dt_str = command[command.index(timeCommand) + len(timeCommand): ending]

            for f in timeFormats:
                try:
                    time = datetime.strptime(dt_str, f["format"])
                    if f["replace"] is not None:
                        for r in f["replace"]:
                            if r == "y":
                                time = time.replace(year=datetime.now().year)
                            if r == "m":
                                time = time.replace(month=datetime.now().month)
                            if r == "d":
                                time = time.replace(day=datetime.now().day)
                    break
                except Exception as e:
                    logger.debug(
                        "Alarm module (user_id:{}): Exception occurred while parsing time format {} - {}"
                            .format(user_id, f, e.message))

        if command.find(userCommand) >= 0:
            ending = len(command)
            if command.find(textCommand, command.index(userCommand) + len(userCommand)) >= 0:
                ending = command.index(textCommand)

            usr_str = command[command.index(userCommand) + len(userCommand): ending]
            try:
                receiver_id = int(usr_str)
            except:
                receiver_id = usr_str

        if command.find(textCommand) >= 0:
            message = command[command.index(textCommand) + len(textCommand): len(command)]

        friends = self.user.get_all_friends(["domain"])

        is_friend = False
        for friend in friends["items"]:
            if isinstance(receiver_id, (int, long)):
                if friend["id"] == receiver_id:
                    is_friend = True
                    break
            elif friend["domain"] == receiver_id:
                is_friend = True
                break

        if not is_friend:
            self.user.send_message(text=random.choice(self.config["responds_on_not_friends"]),
                                   chatid=chat_id, userid=user_id)
            return

        if time is None:
            time = datetime.now() + timedelta(seconds=30)
        elif time < datetime.now():
            self.user.send_message(text=random.choice(self.config["responds_on_past_alarm"]),
                                   chatid=chat_id, userid=user_id)
            return

        new_alarm = {"chat_id": chat_id, "user_id": receiver_id, "time": time, "message": message}

        for alarm_id in self.alarms:
            if new_alarm == self.alarms[alarm_id]:
                logger.debug(
                    "Alarm module (user_id:{}): Alarm (time:{}, message:{}) is already set!"
                        .format(user_id, message))
                return

        self.alarms[len(self.alarms)] = new_alarm
        self.set_alarm_clock(len(self.alarms) - 1)
        self.save_alarms(chat_id or user_id)

        self.user.send_message(text=random.choice(self.config["responds_on_ok"]),
                               chatid=chat_id, userid=user_id)
