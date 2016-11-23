#!/usr/bin/python
# -*- coding: utf-8 -*-


# TODO: can this be different??
MAP_SIZE = 10

MAP_EXAMPLE = """
                0 0 0 1 0 0 3 0 0 1
                2 2 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 3 0 0 2
                0 0 1 0 0 0 0 0 0 2
                0 0 0 0 0 0 0 0 0 0
                0 0 4 4 4 4 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 3 3 3 0 1 0
                0 0 0 0 0 0 0 0 0 0
                """

TMP_TULEN_MAP = """
                0 0 0 1 0 0 3 0 0 1
                2 2 0 0 0 0 3 0 0 0
                0 0 0 0 0 0 3 0 0 2
                0 0 1 0 0 0 0 0 0 2
                0 0 0 0 0 0 0 0 0 0
                0 0 4 4 4 4 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 0 0 0 0 0 0
                0 0 0 0 3 3 3 0 1 0
                0 0 0 0 0 0 0 0 0 0
                """

# answers  =============================================================================================================
INVALID_ANSWER_FORMAT_MSG = u"Неправильный формат ответа"
INVALID_ANSWER_NUMBER_MSG = u"Неправильный номер ответа"
INVALID_ANSWER_TEXT_MSG = u"Неверный ответ! Можете стрелять, но баллов вам не положено"
QUESTION_ALREADY_ANSWERED = u"Вы уже отвечали на вопрос {}"
IMPOSSIBLE_DURING_GAME = u"Невозможно выполнить эту команду во время игры"
IMPOSSIBLE_WITHOUT_GAME = u"Вы ещё не начали игру. Для начала введите Играю в морской бой с ИМЯ_КОМАНДЫ_ОППОНЕНТА"

CORRECT_ANSWER_MSG = u"Ответ верен! Можете стрелять! За попадание получите {} очков"
WAITING_FOR_OPPONENT_MSG = u"Ждем оппонета {}"

UNKNOWN_TEAM_MSG = u"Команда {} не зарегистрирована"
INVALID_OPPONENT_MSG = u"Неизветный противник"
GAME_STARTED_MSG = u"Игра начата с командой {}. Могете стрелять, капитан"


NOT_REGISTERED_YET_MSG = u"Для игры в Морской Бой нужно зарегистрироватся. Напишите Я капитан команды ИМЯ_КОММАНДЫ"
NO_MAP_YET_MSG = u"Нужно загрузить карту. Напишите Загрузи карту [МАССИВ_КАРТЫ]\n" \
                 u"Подсказка: размер массива - 100 чисел подряд через пробел, число 0 - пустое место, числа 1-4 - корабли"
NO_OPPONENT_SET_MSG = u"Для игры нужно выбрать противника. Напишите Играю в морской бой с ИМЯ_КОМАНДЫ_ОППОНЕНТА"
NO_ANSWER_PROVIDED_MSG = u"Для выстрела нужно ответить на вопрос. Напишите Ответ НОМЕР_ВОПРОСА СЛОВО_ИЛИ_ЦИФРА"

ALREADY_REGISTERED_MSG = u"Команда {} уже зарегистрирована"
ALREADY_CAPTAIN_MSG = u"Вы уже являетесь капитаном"
OPPONENT_IS_WAITING_MSG = u"Команда {} ожидает вас как оппонента!"
TEAM_NOT_WAITING_FOR_ANY_OPPONENT_MSG = u"Команда {} не ожидает никаких оппонентов"
TEAM_NOT_WAITING_FOR_OPPONENT_MSG = u"Команда {} не ожидает оппонента {}, но ожидает {}"
TEAM_NAME_IS_EMPTY_MSG = u"Не могу зарегистрировать команду без имени!"
REGISTRATION_OK_MSG = u"Норм все, давай дальше"
REGISTERED_TEAM_MSG = u"Зарегал команду {} с капитаном (uid {})"
OPPONENT_IS_ALREADY_SET_MSG = u"У вас уже есть оппонент {}"
OPPONENT_SET_OK_MSG = u"Команде (team_name {}, team_uid {}) успешно выставлен оппонент (team_name {}, team_uid {})"

INVALID_MAP_MSG = u"Неверная карта"
GOOD_MAP_MSG = u"Карта загружена"
MAP_ALREADY_UPLOADED_MSG = u"Карта уже загружена"

SESSION_ALREADY_ACTIVE_MSG = u"Сессия игры уже активна для uid {}"
SESSION_STARTED_MSG = u"Сессия игры Морской Бой начата для uid {}"
SESSION_NOT_ACTIVE_MSG = u"Сессия не активна для uid {}"
SESSION_STOPPED_MSG = u"Сессия игры Морксой бой остановлена для uid {}"
# answers  =============================================================================================================

# commands  ===================================================================
start_game_processing_command = u"тюлень, хотим в морской бой"
stop_game_processing_command = u"мы закончили морской бой"
answer_command = u"ответ"
gameRequest_command = u"играю в морской бой с"
attack_command = u"атакую:"
questions_command = u"вопросы"
loadMap_command = u"загрузи карту"
registerTeam_command = u"я капитан команды"
