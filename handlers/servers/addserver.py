import logging
from urllib import response
from aiogram import Bot , Dispatcher , executor , types
from aiogram.types.message import ContentType
import requests
import asyncio
import pymongo
from datetime import timedelta, date
import wgconfig.wgexec as wgexec
import random
from main import dp, USLUGI_DB, bot

# Настройки доступа к серверу
from .serverlist import srv1_rus_1_url as URL, HEADERS as HEADERS

@dp.callback_query_handler(text = "add_srv1_rus_1")
async def add_srv1_rus_1 (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    n = 1
    while True:
        presharedkey = wgexec.generate_presharedkey()
        ipv4 = random.randint(2, 254)
        DATA = {
            'allowed_ips': [
                f'10.10.1.{ipv4}/32',
            ],
            'preshared_key': presharedkey,
        }
        ipv4 = f"10.10.1.{ipv4}/32"
        if USLUGI_DB.find_one({"telegram_id": call.from_user.id}) is not None:
            public_key = ''
            data_old = (requests.get(url=URL, headers=HEADERS)).json()
            for gays in USLUGI_DB.find({"telegram_id": call.from_user.id}):
                presharedkey_old = gays['preshared_key']
                for i in data_old:
                    if i['preshared_key']  == presharedkey_old:
                        public_key = i["url_safe_public_key"]
                        requests.delete(url=f'{URL}{public_key}/', headers=HEADERS)
                        USLUGI_DB.delete_one({"telegram_id": call.from_user.id, "preshared_key": presharedkey_old})
        if USLUGI_DB.find_one({"tarif_ip": ipv4}) is None and USLUGI_DB.find_one({"tarif_key": presharedkey}) is None and USLUGI_DB.find_one({"telegram_id": call.from_user.id} ) is None:
            post = {
                "telegram_id": call.from_user.id,
                "tarif_ip": ipv4,
                "preshared_key": presharedkey,
                "srv_id": "srv1_rus_1",
            }
            USLUGI_DB.insert_one(post)
            requests.post(url=URL, headers=HEADERS, json=DATA)
            await bot.send_message(chat_id = call.from_user.id, text = 'Аккаунт создан!\nЗайдите в "МОЙ ТАРИФ"')
            break
        else:
            print (f"Конфликт выдачи аккаунта, попытка решения {n}")
            n += 1
            await asyncio.sleep(1)
            if n == 10:
                await bot.send_message(chat_id = call.from_user.id, text = f'Ошибка выдачи доступа, пожалуйста обратитесь в тех.поддержку\n\nСообщите свой ID агенту тех.поддержки: {call.from_user.id}')
                break