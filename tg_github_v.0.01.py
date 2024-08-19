import os

import telebot
import pandas as pd
from telebot import types


from g4f.client import Client


bot = telebot.TeleBot('') #Обычная версия


"""
UPDATE
11/08 - Запуск постоянно работающего бота для портфолио.
        Создано лого, изменено описание, исправлена орфография
27/07 - Изменена логика сохранения данных пользователей. Теперь они сортируются по папкам. 
        Добавлена возможность сохранять карты/фото и задавать им названия   
26/07 - Добавлен AI ассистент. Добавлена экранная клавиатура. Версия бота - 0.01v
25/07 - Добавлена возможность создавать и удалять заметки
23/07 - настроена функция учета ккал, Добавлен трай эксепт на все функции в main func
22/07 - настроена функция учета доходов
21/07 - настроена функция учета расходов и памяти бота. Версия бота - 0.001v
20/07 - запущен бот
"""


class Ivatar:
    level = {
        'Расход':("Какая стоимость Вашей покупки", "На что потратили", "Правильно ли Я все записал"),
        'Знакомство':('Как Вас называть',),
        'Доход': ('Сколько заработали', 'Опишите Ваш доход', 'Правильно ли Я все записал'),
        'Кошелек': ('Желаете продолжить вывод истории', 'Желаете отредактировать историю', 'Список на удаление', 'Вы подтверждате следующие пункты'),
        'Очистка': ('Кошелек',),
        'Ккал': ('Внести', 'Установить норму', 'Сброс', 'Сохранить историю'),
        'Заметки': ('Добавить', 'Удалить', 'Удалить_1', 'очистка', 'закрепить'),
        'AI': ('ИИ',),
        'CARDS': ('Добавить фото', 'Добавить название', 'Показать', 'Удалить')
    }

    def __init__(self, message):
        self.id = str(message.chat.id) #id с тг
        self.name = None #пользователь определяет, как себя называть

        self.wallet = 0 #начальный баланс кошелька
        self.id_for_wallet_h = 0  # id необходимый для записи трат и доходов
        self.wallet_history = {} #Словарь с историей трат

        self.kkal = 0  #Ежедневная норма ккал
        self.now_kkal = 0 #Остаточная норма
        self.progress_kkal = 0 #Прогресс

        self.level_global = None #Глобальное название задачи
        self.level = None #Локальный этап задачи
        self.cash = dict() #записывается кэш, чтобы не потерять прогресс в задачи

        self.notes = [] #Заметки
        self.notes_main = None #Выделение главной заметки для экрана /info

        self.card = [] #Cards

    """Денежный блок"""
    def money_sell(self, sell, disc): #денежные траты
        self.id_for_wallet_h += 1
        self.wallet -= sell
        new = {f"{self.id_for_wallet_h}": (f'Расход: {sell}', disc)}
        self.wallet_history = new | self.wallet_history

    def money_earn(self, earn, disc): #денежный заработок
        self.id_for_wallet_h += 1
        self.wallet += earn
        new = {f"{self.id_for_wallet_h}": (f'Доход: {earn}', disc)}
        self.wallet_history = new | self.wallet_history

    def show_wallet_history(self, number=0):
        key = list(self.wallet_history.keys())[number]
        return self.wallet_history[key]

    def del_wallet_history(self, n):
        key = list(self.wallet_history.keys())[n]
        del self.wallet_history[key]

    def clear_wallet_history(self):
        self.wallet_history = {}
        self.wallet = 0

    """Ккал БЛОК"""
    def have_kkal(self, kkal): #Прием пищи
        self.now_kkal -= kkal

    def save_kkal(self):
        self.progress_kkal -= self.now_kkal
        self.now_kkal = self.kkal

    def clear_kkal(self):
        self.progress_kkal = 0
        self.kkal = 0
        self.now_kkal = 0

    '''NOTES'''
    def notes_add(self, title, disc):
        self.notes.append([title, disc])

    """Настройки программы"""
    def level_refresh(self): #Позволяет выполнить сброс задачи
        self.level = None
        self.level_global = None

    def cash_level(self, k, v): #Записывает временный кэш
        self.cash[k] = v

    def cash_clear(self): #очищает временные данные
        self.cash = {}

    @staticmethod
    def load(message): #Загрузка пользователя
        user = Ivatar(message)
        data = pd.read_json(f"user/{user.id}/{user.id}")
        for i, k in data.values:
            user.__dict__[i] = k
        return user

    @staticmethod #Сохранение пользователя
    def save_f(user):
        data = pd.DataFrame(user.__dict__.items(), columns=('key', 'value'))
        data.to_json(f"user/{user.id}/{user.id}", index=False)


    @staticmethod #Создание нового пользователя
    def create_file(message):
        user = Ivatar(message)

        if not os.path.isdir(f'user/{user.id}'):
            os.mkdir(f'user.{user.id}')

        data = pd.DataFrame(user.__dict__.items(), columns=('key', 'value'))
        print(data)
        print(user.id)
        data.to_json(f"user/{user.id}/{user.id}", index=False)


""" Скрипты для ТГ """
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, f'При первом запуске автоматически прожимается команда /start\n'
                                      f'Она автоматически инициализирует пользователя. Если ранее пользователь был '
                                      f'создан, то удаляет все данные\n\n'
                                      f'После создания пользователя, рекомендуется выполнить команду /name\n'
                                      f'Так бот поймет, как к Вам можно обращаться')

    bot.send_message(message.chat.id, f'Полезные команды:\n\n'
                                      f'1) /main - открывает главный экран, с которого происходит полное взаимодействие с ботом при помощи экранной клавиатуры\n\n'
                                      f'2) /stop - пиши ее в любой момент, когда бот начинает тупить или была прописана неверная команда\n\n')

    bot.send_message(message.chat.id, f'Если возникли вопросы или был замечен баг, то милости просим в лс @dan1k61')

@bot.message_handler(commands=['start'])
def start(message):
    Ivatar.create_file(message)
    bot.send_message(message.chat.id,   f'Личный помощник успешно запущен')


@bot.message_handler(commands=['stop']) #Сбрасывает Кэш и Уровень задачи.
def stop(message):
    user = Ivatar.load(message)
    user.level_refresh()
    user.cash_clear()
    Ivatar.save_f(user)
    bot.send_message(message.chat.id, f'Прогресс сброшен, {user.name}')


@bot.message_handler(commands=['main'])
def main(message):
    user = Ivatar.load(message)

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/Food')
    btn2 = types.KeyboardButton('/Wallet')
    btn3 = types.KeyboardButton('/Notes')
    btn4 = types.KeyboardButton('/AI')
    btn5 = types.KeyboardButton('/Cards')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)

    if user.level is not None: #Проверка на выполнение задачи
        bot.send_message(message.chat.id, f'{user.name}, cейчас выполняется задача:, {user.level_global}\n'
                                          f'/stop - чтобы прекратить выполнение задачи')
    else:
        bot.send_message(message.chat.id, f'{user.name}, на данный момент я свободен')

    bot.send_message(message.chat.id, f'Food\n\nОстаток ккал на день: {user.now_kkal}\n'
                                      f'Текущий прогресс: {user.progress_kkal}\n')

    bot.send_message(message.chat.id, f'Wallet\n\nОстаток средств на карте: {user.wallet}\n')

    if user.notes_main is not None: #Проверка на закрепленную заметку
        bot.send_message(message.chat.id, f'Notes\n\n{user.notes_main[0]}\n'
                                          f'{user.notes_main[1]}', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, f'Notes\n\nНа данный момент нет закрепленной заметки', reply_markup=markup)


@bot.message_handler(commands=['name'])
def main(message):
    user = Ivatar.load(message)
    user.level = Ivatar.level['Знакомство'][0]
    user.level_global = "Знакомство"
    bot.send_message(message.chat.id,   f'{Ivatar.level['Знакомство'][0]}?')
    Ivatar.save_f(user)


"""_________________________________________WALLET_________________________________________"""


@bot.message_handler(commands=['Wallet'])
def wallet(message):
    user = Ivatar.load(message)
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton('Расход', callback_data='расход_кошелек')
    btn2 = types.InlineKeyboardButton('Доход', callback_data='доход_кошелек')
    btn3 = types.InlineKeyboardButton('История', callback_data='история_кошелек')
    btn4 = types.InlineKeyboardButton('Изменение Истории', callback_data='изменение_кошелек')
    btn5 = types.InlineKeyboardButton('Очистка', callback_data='очистка_кошелек')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    markup.row(btn5)

    bot.send_message(message.chat.id, f'{user.name}, добро пожаловать в меню Кошелек. Что будете делать?', reply_markup=markup)


"""________________________________kkal______________________________________________"""


@bot.message_handler(commands=['Food'])
def food(message):
    user = Ivatar.load(message)
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton('Установить норму ккал', callback_data='норма_ккал')
    btn2 = types.InlineKeyboardButton('Внести прием пищи', callback_data='пища_ккал')
    btn3 = types.InlineKeyboardButton('Сохранить результат', callback_data='сохранить_ккал')
    btn4 = types.InlineKeyboardButton('Выполнить сброс', callback_data='сброс_ккал')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)

    bot.send_message(message.chat.id, f'{user.name}, Вы находитесь в меню ККАЛ. Что бы Вы хотели выполнить?', reply_markup=markup)


"""______________________________________NOTE__________________________________________"""


@bot.message_handler(commands=['Notes'])
def notes(message):
    user = Ivatar.load(message)
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton('Добавить заметку', callback_data='заметки_добавить')
    btn2 = types.InlineKeyboardButton('Просмотреть заметки', callback_data='заметки_просмотреть')
    btn3 = types.InlineKeyboardButton('Снять закреп', callback_data='заметки_снять')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)

    bot.send_message(message.chat.id, f'{user.name}, Вы находитесь в меню ЗАМЕТКИ. Что бы Вы хотели выполнить?',
                     reply_markup=markup)


"""_________________________________AI_________________________________________________"""

@bot.message_handler(commands=['AI'])
def II(message):
    user = Ivatar.load(message)
    user.level_global = "AI"
    user.level = Ivatar.level['AI'][0]
    Ivatar.save_f(user)
    bot.send_message(message.chat.id, f'{user.name}, задайте любой вопрос, а я попробую найти на него ответ.'
                                      f'Предупреждаю, что есть задержка между запросом и ответом, поэтому не стоит спамить.')


"""_________________________________CARDS__________________________________________"""


@bot.message_handler(commands=['Cards'])
def cards(message):

    user = Ivatar.load(message)
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton('Показать карты', callback_data='Карты_показать')
    btn2 = types.InlineKeyboardButton('Загрузить карту', callback_data='Карты_загрузить')
    btn3 = types.InlineKeyboardButton('Удалить карту', callback_data='Карты_удалить')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)

    bot.send_message(message.chat.id, f'{user.name}, Вы находитесь в меню Карты. Что бы Вы хотели выполнить?',
                     reply_markup=markup)


"""_________________________________CALL BACK__________________________________________"""


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    user = Ivatar.load(callback.message)

    # Ккал
    if callback.data == 'норма_ккал':
        bot.send_message(callback.message.chat.id, f'{user.name}, Введите ежедневную норму ккал')
        user.level_global = 'Ккал'
        user.level = Ivatar.level['Ккал'][1] #Установка нормы
        Ivatar.save_f(user)

    elif callback.data == 'пища_ккал':
        bot.send_message(callback.message.chat.id, f'{user.name}, Сколько ккал Вы съели?')
        user.level_global = 'Ккал'
        user.level = Ivatar.level['Ккал'][0]  #Внести пищу
        Ivatar.save_f(user)

    elif callback.data == 'сохранить_ккал':
        bot.send_message(callback.message.chat.id, f'Сохранение ккал пеернесет их в результат. \n'
                                                   f'Остаток ежедневной нормы станет {user.kkal}\n'
                                                   f'Желаете сохранить результат?\n\n /stop - для отмены')
        user.level_global = 'Ккал'
        user.level = Ivatar.level['Ккал'][3]  # Сохранить результат
        Ivatar.save_f(user)

    elif callback.data == 'сброс_ккал':
        bot.send_message(callback.message.chat.id, f'{user.name}, Вы уверены, что хотите выполнить сброс?\n'
                                                   f'Прогресс и ежедневная норма будут сброшены в 0\n\n'
                                                   f'/stop - для отмены')
        user.level_global = 'Ккал'
        user.level = Ivatar.level['Ккал'][2]  # Выполнить сброс
        Ivatar.save_f(user)

    # Кошелек
    elif callback.data == 'расход_кошелек':
        user.level = Ivatar.level['Расход'][0]
        user.level_global = "Расход"
        bot.send_message(callback.message.chat.id, f'{Ivatar.level["Расход"][0]}, {user.name}?')
        Ivatar.save_f(user)

    elif callback.data == 'доход_кошелек':
        user.level = Ivatar.level['Доход'][0]
        user.level_global = "Доход"
        bot.send_message(callback.message.chat.id, f'{Ivatar.level["Доход"][0]}, {user.name}?')
        Ivatar.save_f(user)

    elif callback.data == 'история_кошелек':
        user.level_global = 'Кошелек'
        user.level = Ivatar.level["Кошелек"][0]

        bot.send_message(callback.message.chat.id, f'{user.name}, Ваш текущий баланс: {user.wallet}\n')
        bot.send_message(callback.message.chat.id, f'История платежей:\n')

        for i in range(5):
            if i == len(user.wallet_history):
                bot.send_message(callback.message.chat.id, f'{user.name} История полностью показана')
                return

            bot.send_message(callback.message.chat.id, f'{i}. {user.show_wallet_history(i)[0]} {user.show_wallet_history(i)[1]}')

        user.cash['продолжение'] = 5
        Ivatar.save_f(user)
        bot.send_message(callback.message.chat.id, f'\n{user.name}, {Ivatar.level["Кошелек"][0]}?')

    elif callback.data == 'изменение_кошелек':
        bot.send_message(callback.message.chat.id, f'{Ivatar.level["Кошелек"][1]}?')
        user.level_global = 'Кошелек'
        user.level = Ivatar.level["Кошелек"][1]
        Ivatar.save_f(user)

    elif callback.data == 'очистка_кошелек':
        bot.send_message(callback.message.chat.id,
                         f'{user.name}, Вы подтверждаете полную очистку истории кошелька? '
                         f'Вся история и текущий баланс будут обнулены\n\n'
                         f'/stop для отмены')
        user.level_global = 'Очистка'
        user.level = Ivatar.level['Очистка'][0]
        Ivatar.save_f(user)

    # Заметки
    elif callback.data == 'заметки_добавить':
        user.level = Ivatar.level['Заметки'][0]
        user.level_global = 'Заметки'
        bot.send_message(callback.message.chat.id, f'Напишите название заметки')
        Ivatar.save_f(user)

    elif callback.data == 'заметки_просмотреть':
        if len(user.notes) != 0:
            for i, n in enumerate(user.notes):
                bot.send_message(callback.message.chat.id, f'{i}. Название: {n[0]}\nОписание: {n[1]}')
        else:
            bot.send_message(callback.message.chat.id, f'Список пуст')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Добавить заметку', callback_data='заметки_добавить')
        btn2 = types.InlineKeyboardButton('Закрепить заметку', callback_data='заметки_закрепить')
        btn3 = types.InlineKeyboardButton('Удалить заметку', callback_data='заметки_редактировать')
        btn4 = types.InlineKeyboardButton('Очистить все заметки', callback_data='заметки_очистка')
        markup.row(btn1)
        markup.row(btn2)
        markup.row(btn3)
        markup.row(btn4)

        bot.send_message(callback.message.chat.id, f'Что бы вы хотели сделать?', reply_markup=markup)

    elif callback.data == 'заметки_редактировать':
        user.level = Ivatar.level['Заметки'][2]
        user.level_global = 'Заметки'
        bot.send_message(callback.message.chat.id, f'Введите номер заметки, который хотели бы удалить')
        Ivatar.save_f(user)

    elif callback.data == 'заметки_очистка':
        user.level = Ivatar.level['Заметки'][3]
        user.level_global = 'Заметки'
        bot.send_message(callback.message.chat.id, f'Вы уверены, что хотите очистить все заметки?\n\n'
                                                   f'/stop - для отмены')
        Ivatar.save_f(user)

    elif callback.data == 'заметки_закрепить':
        user.level = Ivatar.level['Заметки'][4]
        user.level_global = 'Заметки'
        bot.send_message(callback.message.chat.id, f'Введите номер, который хотие закрепить')
        Ivatar.save_f(user)

    elif callback.data == 'заметки_снять':
        if user.notes_main is not None:
            user.notes_main = None
            bot.send_message(callback.message.chat.id, f'{user.name}, закреп снят')
            Ivatar.save_f(user)
        else:
            bot.send_message(callback.message.chat.id, f'{user.name}, нет закрепленной заметки')

    #Карты
    elif callback.data == 'Карты_загрузить':
        user.level = Ivatar.level['CARDS'][0]
        user.level_global = 'CARDS'
        bot.send_message(callback.message.chat.id, f'{user.name}, загрузите одну фотографию, которую хотите сохранить')
        Ivatar.save_f(user)

    elif callback.data == 'Карты_показать':

        if len(user.card) > 0:
            bot.send_message(callback.message.chat.id,
                             f'{user.name}, введите номер карты, фотографию которой хотите получить')

            for i, name in enumerate(user.card):
                bot.send_message(callback.message.chat.id, f'{i}. {name[0]}')

            user.level = Ivatar.level['CARDS'][2]
            user.level_global = 'CARDS'
            Ivatar.save_f(user)

        else:
            bot.send_message(callback.message.chat.id, f'Коллекция карт пуста')

    elif callback.data == 'Карты_удалить':

        if len(user.card) > 0:
            bot.send_message(callback.message.chat.id,
                             f'{user.name}, введите номер карты, которую хотите удалить')

            for i, name in enumerate(user.card):
                bot.send_message(callback.message.chat.id, f'{i}. {name[0]}')

            user.level = Ivatar.level['CARDS'][3]
            user.level_global = 'CARDS'
            Ivatar.save_f(user)

        else:
            bot.send_message(callback.message.chat.id, f'Коллекция карт пуста')


    else:
        bot.send_message(callback.message.chat.id, f'{user.name}, Команда еще не реализована')


"""_________________________________MAIN FUNC__________________________________________"""
@bot.message_handler(content_types=["photo"])
def photo(message):
    user = Ivatar.load(message)

    if user.level_global == 'CARDS':
        user.cash_level('Фото', message.photo[-1].file_id)
        user.level = Ivatar.level['CARDS'][1]
        Ivatar.save_f(user)
        bot.send_message(message.chat.id, f'Напишите название карты')


@bot.message_handler()
def main(message):
    user = Ivatar.load(message)
    try:
        if user.level_global in ('Знакомство', 'Расход', 'Доход', 'Кошелек', 'Очистка'):
            work_1(message)

        elif user.level_global == 'Ккал':
            kkal_block(message)

        elif user.level_global == 'Заметки':
            note(message)

        elif user.level_global == 'AI':
            AI(message)

        elif user.level_global == 'CARDS':
            card(message)

        else:
            bot.send_message(message.chat.id,
                             f'{user.name}, Не понимаю вашего запроса')
    except:
        bot.send_message(message.chat.id, f'{user.name}, Боюсь вы попали на ошибку.'
                                          f'Попробуйте заново написать сообщение или сбросте текущий прогресс с помощью команды /stop> и повторить запрос заново. '
                                          f'Возможно, создатель внес некие изменения в код, которые решатся только созданием нового пользователя с помощью команды /start\n\n'
                                          f'Если ошибка повторится, отправьте скрины запросов и необходимую информацию в чат @dan1k61 ')


"""Знакомство + кошелек"""
def work_1(message):
    """
    Блок знакомства, Доходов и Расходов

    Расходы состоят из трех этапов:
    1) Бот узнает стоимость
    2) Бот узнает описание
    3) Если все верно добавляет запись и очищает кэш

    Блок доходов:
    1) Бот узнает сумму
    2) Бот узнает описание
    3) Если все верно добавляет запись и очищает кэш

    Вывод информации кошелька

    Блок знакомств:
    Бот узнает, как Вас называть
    """
    user = Ivatar.load(message)
    if user.level_global == "Знакомство":

        if user.level == Ivatar.level['Знакомство'][0]:
            user.name = str(message.text)
            user.level_refresh()
            bot.send_message(message.chat.id, f"Приветсвую Вас, {user.name}")
            Ivatar.save_f(user)
            return

    """Блок Расхода"""
    if user.level_global == "Расход":

        if user.level == Ivatar.level['Расход'][0]:
            user.cash_level('Стоимость покупки', int(message.text)) # Запись в буфер обмена
            user.level = Ivatar.level['Расход'][1]
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'{Ivatar.level['Расход'][1]}, {user.name}') #Отправка соо ботом
            return

        if user.level == Ivatar.level['Расход'][1]:
            user.cash_level("Описание покупки", message.text) # Запись в буфер обмена
            user.level = Ivatar.level['Расход'][2]
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'Цена: {user.cash["Стоимость покупки"]}\n'
                                              f'Описание: {user.cash["Описание покупки"]}\n\n'
                                              f'Я Правильно все записал?') #Отправка соо ботом
            return

        if user.level == Ivatar.level['Расход'][2]:
            if message.text.lower() == 'да':
                user.money_sell(user.cash["Стоимость покупки"], user.cash["Описание покупки"])
                Ivatar.save_f(user)
                bot.send_message(message.chat.id, f'Запись успешно сохранена') #Отправка соо ботом

                user.level_refresh() # Очистка временной памяти
                user.cash_clear()
                Ivatar.save_f(user)
                user = None
                return

            if message.text.lower() == 'нет':
                bot.send_message(message.chat.id, f'В таком случае, начинаем заново, либо введите команду /stop') #Отправка соо ботом

                user.level_refresh() # Очистка временной памяти
                user.cash_clear()
                Ivatar.save_f(user)
                user = None
                return

        else:
            bot.send_message(message.chat.id, f'Меня еще не научили распозновать такой вид сообщения :(') #Отправка соо ботом

    """Блок дохода"""
    if user.level_global == "Доход":
        if user.level == Ivatar.level['Доход'][0]:
            user.cash_level('Деньги', int(message.text)) # Запись в буфер обмена
            user.level = Ivatar.level['Доход'][1]
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'{Ivatar.level['Доход'][1]}, {user.name}') #Отправка соо ботом
            return

        if user.level == Ivatar.level['Доход'][1]:
            user.cash_level("Описание", message.text) # Запись в буфер обмена
            user.level = Ivatar.level['Доход'][2]
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'Сумма: {user.cash["Деньги"]}\n'
                                              f'Описание: {user.cash["Описание"]}\n\n'
                                              f'Я Правильно все записал?') #Отправка соо ботом
            return

        if user.level == Ivatar.level['Доход'][2]:
            if message.text.lower() == 'да':
                user.money_earn(user.cash["Деньги"], user.cash["Описание"]) #Функция записи денежных средств
                Ivatar.save_f(user)
                bot.send_message(message.chat.id, f'Запись успешно сохранена') #Отправка соо ботом

                user.level_refresh() # Очистка временной памяти
                user.cash_clear()
                Ivatar.save_f(user)
                return

            if message.text.lower() == 'нет':
                bot.send_message(message.chat.id, f'В таком случае, начинаем заново, либо введите команду /stop') #Отправка соо ботом

                user.level_refresh() # Очистка временной памяти
                user.cash_clear()
                Ivatar.save_f(user)
                return

        else:
            bot.send_message(message.chat.id, f'Меня еще не научили распозновать такой вид сообщения :(') #Отправка соо ботом

    '''Вывод информации кошелька'''
    if user.level_global == "Кошелек":

        if message.text.lower() == 'нет':
            bot.send_message(message.chat.id, f'{user.name}, Задача завершена')
            user.cash_clear()
            user.level_refresh()
            Ivatar.save_f(user)
            return

        if message.text.lower() == 'да' and user.level == Ivatar.level["Кошелек"][0]:
            for i in range(user.cash['продолжение'], user.cash['продолжение']+5):

                if i == len(user.wallet_history):
                    bot.send_message(message.chat.id, f'{user.name}, История полностью показана')
                    bot.send_message(message.chat.id, f'{Ivatar.level["Кошелек"][1]}?') #Отпраляет предложение на редактирование истории
                    user.cash_clear()
                    user.level = Ivatar.level["Кошелек"][1]
                    Ivatar.save_f(user)
                    return

                bot.send_message(message.chat.id, f'{i}. {user.show_wallet_history(i)[0]} {user.show_wallet_history(i)[1]}')
            user.cash['продолжение'] = 5
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'\n{user.name}, {Ivatar.level["Кошелек"][0]}?')
            return

        if message.text.lower() == 'да' and user.level == Ivatar.level["Кошелек"][1]:
            bot.send_message(message.chat.id, f'Введите номера через пробел, чью историю Вы бы желали удалиить {user.name}')
            user.level = Ivatar.level["Кошелек"][2] #Переход на уровень подтверждения
            Ivatar.save_f(user)
            return

        if user.level == Ivatar.level["Кошелек"][2]:

            lst = sorted([int(x) for x in message.text.split()])
            user.cash_level('Список на удаление', lst)

            for i in lst: #Проверка на верность ввода данных
                if i > len(user.wallet_history) or type(i) != int:
                    bot.send_message(message.chat.id,
                                     f'Боюсь Вы допустили ошибку. Перечислите номера еще раз {user.name}\n'
                                     f'Пример ответного соощение: 1 2 3')
                    return

            bot.send_message(message.chat.id,f'{Ivatar.level["Кошелек"][3]}?') #Отправляем сообщение для подтверждения
            user.level = Ivatar.level["Кошелек"][3] #Подтверждение списка на удаление
            Ivatar.save_f(user) #Сохранение

            for i in user.cash['Список на удаление']:
                bot.send_message(message.chat.id, f'{i}. {user.show_wallet_history(i)[0]} {user.show_wallet_history(i)[1]}')
            return

        if message.text.lower() == 'да' and user.level == Ivatar.level["Кошелек"][3]:
            for i in user.cash['Список на удаление'][::-1]:
                user.del_wallet_history(i)
            user.level_refresh()
            user.cash_clear()
            Ivatar.save_f(user)
            bot.send_message(message.chat.id, f'{user.name}, пукты были успешно удалены')
            return

        else:
            bot.send_message(message.chat.id, f'Меня еще не научили распозновать такой вид сообщения :(') #Отправка соо ботом

    """Очистка"""
    if user.level_global == "Очистка":

        if message.text.lower() == 'да' and user.level == Ivatar.level['Очистка'][0]: #Очистка кошелька
            user.clear_wallet_history()
            bot.send_message(message.chat.id, "История доходов и расходов успешно очищена, а баланс ровняется 0")

            user.level_refresh()
            user.cash_clear()
            Ivatar.save_f(user)


"""Блок учета ккал"""
def kkal_block(message):
    user = Ivatar.load(message)
    if user.level == Ivatar.level['Ккал'][0]:
        user.have_kkal(int(message.text))
        bot.send_message(message.chat.id, f'Я записал прием пищи на {message.text} ккал\n\n'
                                          f'{user.name}, остаточная ежедневная норма: {user.now_kkal}')
        user.level_refresh()
        Ivatar.save_f(user)

    if user.level == Ivatar.level['Ккал'][1]:
        user.kkal = int(message.text) #Установка константы по ккал
        user.now_kkal = user.kkal #Установка ежедневной нормы
        bot.send_message(message.chat.id, f'{user.name}, ежедневная норма установлена в районе: {int(message.text)}')
        user.level_refresh()
        Ivatar.save_f(user)

    if user.level == Ivatar.level['Ккал'][2] and message.text.lower() == 'да':
        bot.send_message(message.chat.id, f'Блок ккал успешно сброшен в 0')
        user.clear_kkal()
        user.level_refresh()
        Ivatar.save_f(user)

    if user.level == Ivatar.level['Ккал'][3] and message.text.lower() == 'да':
        user.save_kkal()
        bot.send_message(message.chat.id, f'Текущий прогресс: {user.progress_kkal}\n'
                                          f'Отрицательное значение свидетельствует дефициту')
        user.level_refresh()
        Ivatar.save_f(user)


"""Блок учета ккал"""
def note(message):
    user = Ivatar.load(message)

    if user.level == Ivatar.level['Заметки'][0]: #Создание заметки этап 1
        user.cash_level('название', message.text)
        bot.send_message(message.chat.id, f'Напишите описание заметки')
        user.level = Ivatar.level['Заметки'][1]
        Ivatar.save_f(user)

    elif user.level == Ivatar.level['Заметки'][1]: #Создание заметки этап 2
        user.notes_add(user.cash['название'], message.text)
        bot.send_message(message.chat.id, f'{user.name}, заметка успешно создана\n\n\n'
                                          f'Название: {user.cash["название"]}\n\n'
                                          f'Описание:\n {message.text}')
        user.level_refresh()
        user.cash_clear()
        Ivatar.save_f(user)

    #Удаляет определенную заметку
    elif user.level == Ivatar.level['Заметки'][2]:
        del user.notes[int(message.text)]
        user.level_refresh()
        Ivatar.save_f(user)

        bot.send_message(message.chat.id, f'{user.name}, заметка успешно удалена')
        notes(message)

    #Удаляет все заметки
    elif user.level == Ivatar.level['Заметки'][3] and message.text.lower() == 'да':
        user.notes.clear()
        user.level_refresh()
        user.notes_main = None
        Ivatar.save_f(user)

        bot.send_message(message.chat.id, f'{user.name}, заметки успешно очищены')
        notes(message)

    elif user.level == Ivatar.level['Заметки'][4]: #Закрепляет заметку на экране /main
        if int(message.text) >= len(user.notes) or int(message.text) < 0:
            raise ValueError
        user.notes_main = user.notes[int(message.text)]
        user.level_refresh()
        Ivatar.save_f(user)
        bot.send_message(message.chat.id, f'{user.name}, заметка успешно закреплена\n'
                                          f'{user.notes_main[0]}')
        notes(message)


"""AI"""
def AI(message):
    user = Ivatar.load(message)
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # model=g4f.models.Bing.model_aliases,
        messages=[{"role": "user", "content": f"В каждом ответе строй обращение ко мне и называй меня {user.name}."
                                              "Переводи свой ответ на Русский"},
                  {"role": "assistant", "content": f"{user.name}, хорошо"},
                  {"role": "user", "content": f"{message.text}"}],
    )
    print(len(response.choices[0].message.content))
    bot.send_message(message.chat.id, f'{response.choices[0].message.content}')


"""CARDS"""
def card(message):
    user = Ivatar.load(message)

    if user.level == Ivatar.level['CARDS'][1]:
        user.card.append((message.text, user.cash['Фото']))
        bot.send_message(message.chat.id, f'{user.name}, карта "{message.text}" успешно добавлена в коллекцию')

        user.level_refresh()
        user.cash_clear()
        Ivatar.save_f(user)

        cards(message)

    if user.level == Ivatar.level['CARDS'][2]:
        bot.send_message(message.chat.id, f'{user.card[int(message.text)][0]}')
        bot.send_photo(message.chat.id, photo=f'{user.card[int(message.text)][1]}')

        user.level_refresh()
        Ivatar.save_f(user)

        cards(message)

    if user.level == Ivatar.level['CARDS'][3]:

        bot.send_message(message.chat.id, f'Карта "{user.card[int(message.text)][0]}" успешно удалена')
        user.card.pop(int(message.text))

        user.level_refresh()
        Ivatar.save_f(user)

        cards(message)


bot.infinity_polling(timeout=10, long_polling_timeout = 5) #nonstop_bot