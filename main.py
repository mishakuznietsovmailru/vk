import sqlite3
import vk_api
import random
import os
import sys
import requests
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkUpload

name = ''

class Data:
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()

    def create(self):
        self.cur.execute('''CREATE TABLE users
                  (user_id text, name text, vorname text, state integer, state_2 integer, true_now integer, 
                  false_now integer, true_total integer, false_total integer, message integer)''')

    def new_user(self, user_id, user_name, vorname):
        self.cur.execute('''INSERT INTO users (user_id, name, vorname, state, state_2, message)
                  VALUES ({}, '{}', '{}', 0, 0, 0, 0, 0, 0, 0)'''.format(user_id, user_name, vorname))
        self.con.commit()

    def get_users(self):
        return self.cur.execute('''SELECT user_id FROM users''').fetchall()

    def get_state(self, user_id):
        return self.cur.execute('''SELECT state FROM users WHERE user_id = {}'''.format(user_id)).fetchall()[0][0]

    def get_state_2(self, user_id):
        return self.cur.execute('''SELECT state_2 FROM users WHERE user_id = {}'''.format(user_id)).fetchall()[0][0]

    def set_state_2(self, id, number):
        self.cur.execute('''UPDATE users SET state_2 = {} WHERE user_id = "{}"'''.format(number, id))
        self.con.commit()

    def set_state(self, id, number):
        self.cur.execute('''UPDATE users SET state = {} WHERE user_id = "{}"'''.format(number, id))

    def true_now(self, id):
        n = self.cur.execute('''SELECT true_now FROM users WHERE user_id = "{}"'''.format(str(id))).fetchall()[0][0]
        n = int(n) + 1
        self.cur.execute('''UPDATE users SET true_now = {} WHERE user_id = "{}"'''.format(n, str(id)))
        self.con.commit()
        return n

    def false_now(self, id):
        n = self.cur.execute('''SELECT false_now FROM users WHERE user_id = "{}"'''.format(str(id))).fetchall()[0][0]
        n = int(n) + 1
        self.cur.execute('''UPDATE users SET false_now = {} WHERE user_id = "{}"'''.format(n, str(id)))
        self.con.commit()
        return n

    def true_total(self, id):
        n = self.cur.execute('''SELECT true_total FROM users WHERE user_id = "{}"'''.format(str(id))).fetchall()[0][0]
        n = int(n) + 1
        self.cur.execute('''UPDATE users SET true_total = {} WHERE user_id = "{}"'''.format(n, str(id)))
        self.con.commit()

    def false_total(self, id):
        n = self.cur.execute('''SELECT false_total FROM users WHERE user_id = "{}"'''.format(str(id))).fetchall()[0][0]
        n = int(n) + 1
        self.cur.execute('''UPDATE users SET false_total = {} WHERE user_id = "{}"'''.format(n, str(id)))
        self.con.commit()

    def true_0(self, uid):
        self.cur.execute('''UPDATE users SET true_now = 0 WHERE user_id = "{}"'''.format(uid))
        self.con.commit()

    def false_0(self, uid):
        self.cur.execute('''UPDATE users SET false_now = 0 WHERE user_id = "{}"'''.format(uid))
        self.con.commit()




class Maps:
    def get_map(self, coord, scale):
        response = None
        map_request = "http://static-maps.yandex.ru/1.x/?ll={},{}&spn={},{}&l=sat".format(coord[0],
                                                                                          coord[1], scale[0], scale[1])
        # map_request = "http://static-maps.yandex.ru/1.x/?ll=135.530887,-25.703118&spn=25,25&l=sat"
        response = requests.get(map_request)
        if not response:
            ''' отправить картинку с ошибкой'''
            pass
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        print('well')


d = Data('data.db')
d.true_now(465416009)
# d.create()
lands = {'Австралия': [[135.530887, -25.7031188], [25, 25]],
         'Испания': [[-2.7231, 39.97], [15, 15]],
         'Италия': [[14.559, 41.033], [15, 15]]}


def main():
    vk_session = vk_api.VkApi(
        token='181e71fd98afa5701ecc7a8962c2cadb90c09b2f550b418f1353dd771ee04d47e1860e7517c1e84614604')
    vk = vk_session.get_api()
    long_poll = VkBotLongPoll(vk_session, 193215617)

    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:

            ids = []
            for elem in d.get_users():
                ids.append(int(elem[0]))
            msg = event.message
            msg['text'] = msg['text'].lower()
            uid = msg.from_id
            if msg['text'][-1] == 'я':
                if msg['text'] == name:
                    d.true_now(uid)
                else:
                    d.false_now(uid)
            if uid not in ids:
                user_get = vk.users.get(user_ids=uid)
                user_get = user_get[0]
                first_name = user_get['first_name']
                last_name = user_get['last_name']
                d.new_user(uid, first_name, last_name)
                vk.messages.send(user_id=uid, message='Добро пожаловать!', keyboard=open('keyboards/start.json', "r",
                                                                                         encoding="UTF-8").read(),
                                 random_id=int(random.randint(2, 2 ** 64)))
            else:
                state = d.get_state(uid)
                print(state)
                if state == 0:
                    print(msg)
                    if msg['text'] == 'угадай страну':
                        d.set_state(uid, 1)
                        d.set_state_2(uid, 5)
                        vk.messages.send(user_id=uid, message='Выбран раздел "угадай страну".'
                                                              ' Чтобы начать нажмите кнопку.',
                                         keyboard=open('keyboards/lander.json', "r",
                                                       encoding="UTF-8").read(),
                                         random_id=int(random.randint(2, 2 ** 64)))
                    elif msg['text'] == 'мой профиль':
                        vk.messages.send(user_id=uid, message='Статистика вашего профиля',
                                         keyboard=open('keyboards/profile.json', "r",
                                                       encoding="UTF-8").read(),
                                         random_id=int(random.randint(2, 2 ** 64)))
                elif state == 1:
                    send_question(vk_session, vk, uid)
                    # if d.get_state_2(uid) > 0:
                    #     q = random.randint(0, len(lands.keys()))
                    #     a = []
                    #     for elem in lands.keys():
                    #         a.append(elem)
                    #     # print(lands.keys())
                    #     # print(a)
                    #     name = a[q - 1]
                    #     # print(name)
                    #     m = Maps()
                    #     m.get_map(lands[name][0], lands[name][1])
                    #     upload = VkUpload(vk_session)
                    #     photo = upload.photo_messages(photos='map.png')[0]
                    #     vk.messages.send(
                    #         user_id=uid,
                    #         message='Какая это страна?',
                    #         attachment='photo{}_{}'.format(photo['owner_id'], photo['id']),
                    #         random_id=int(random.randint(2, 2 ** 64)))
                    #     w = d.get_state_2(uid)
                    #     d.set_state_2(uid, w - 1)
                    if msg['text'] == 'начать1':
                        vk.messages.send(user_id=uid, message='Сколько вопросов вы хотите увидеть в тесте?',
                                         keyboard=open('keyboards/numbers.json', "r",
                                                       encoding="UTF-8").read(),
                                         random_id=int(random.randint(2, 2 ** 64)))

                    elif msg['text'] == '2':
                        d.set_state_2(uid, 2)
                    elif msg['text'] == '5':
                        d.set_state_2(uid, 5)
                    elif d.get_state_2(uid) == 0:
                        a = d.true_now(uid)
                        b = d.false_now(uid)
                        vk.messages.send(user_id=uid, message='Вы завершили тест.\nВаш результат:\n'
                                                              'Правильно - {}, неправильно - {}.'.format(a, b),
                                         keyboard=open('keyboards/numbers.json', "r",
                                                       encoding="UTF-8").read(),
                                         random_id=int(random.randint(2, 2 ** 64)))
                        d.false_0(uid)
                        d.true_0(uid)

            if msg['text'] == 'назад':
                d.set_state(uid, 0)
                vk.messages.send(user_id=uid, message='Вы попали в гланое меню',
                                 keyboard=open('keyboards/start.json', 'r', encoding='UTF-8').read(),
                                 random_id=int(random.randint(1, 2 ** 64)))
                d.false_0(uid)
                d.true_0(uid)


def send_question(vk_session, vk, uid):
    q = random.randint(0, len(lands.keys()))
    a = []
    for elem in lands.keys():
        a.append(elem)
    # print(lands.keys())
    # print(a)
    name = a[q - 1]
    # print(name)
    m = Maps()
    m.get_map(lands[name][0], lands[name][1])
    upload = VkUpload(vk_session)
    photo = upload.photo_messages(photos='map.png')[0]
    vk.messages.send(
        user_id=uid,
        message='Какая это страна?',
        attachment='photo{}_{}'.format(photo['owner_id'], photo['id']),
        random_id=int(random.randint(2, 2 ** 64)))
    w = d.get_state_2(uid)
    d.set_state_2(uid, w - 1)


if __name__ == '__main__':
    main()
