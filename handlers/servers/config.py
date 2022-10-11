from aiogram import Bot , Dispatcher , executor , types
from aiogram.types import InputFile
from aiogram.types.message import ContentType
from handlers.keyboard import markups as nav
import requests
import os
from main import dp, bot, USLUGI_DB
from .serverlist import HEADERS as HEADERS, srv1_rus_1_url as srv1_rus_1_url

params = {'width': '256',}

@dp.callback_query_handler(text = "download_config")
async def download_config (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    if USLUGI_DB.find_one({"telegram_id": call.from_user.id}) is not None:
        preshared_key = USLUGI_DB.find_one({"telegram_id": call.from_user.id})["preshared_key"]
        srv = USLUGI_DB.find_one({"telegram_id": call.from_user.id})["srv_id"]
        match srv:
            case "srv1_rus_1":
                data_old = (requests.get(url=srv1_rus_1_url, headers=HEADERS)).json()
                for gays in USLUGI_DB.find({"telegram_id": call.from_user.id}):
                    preshared_key = gays['preshared_key']
                    for i in data_old:
                        if i['preshared_key']  == preshared_key:
                            public_key = i["url_safe_public_key"]
                with requests.get(f'{srv1_rus_1_url}{public_key}/quick.conf', headers=HEADERS) as r:
                    with open(f'cfg//{call.from_user.id}_{srv}.conf', 'w') as f:
                        f.write(r.text)
                with requests.get(f'{srv1_rus_1_url}{public_key}/quick.conf.png', headers=HEADERS, params=params) as r:
                    with open(f'cfg//{call.from_user.id}_{srv}.png', 'wb') as f:
                        f.write(r.content)
                await bot.send_message(call.from_user.id, 'Ваши данные для подключения!')
                file = open(f'cfg//{call.from_user.id}_{srv}.conf', "rb")
                await bot.send_document(call.from_user.id, document=file)
                file = open(f'cfg//{call.from_user.id}_{srv}.png', "rb")
                await bot.send_photo(call.from_user.id, photo=file)
                if(os.path.isfile(f'cfg//{call.from_user.id}_{srv}.conf')):
                    os.remove(f'cfg//{call.from_user.id}_{srv}.conf')
                if(os.path.isfile(f'cfg//{call.from_user.id}_{srv}.png')):
                    os.remove(f'cfg//{call.from_user.id}_{srv}.png')
    else:
        await bot.send_message(call.from_user.id, 'Аккаунт не найден!')

@dp.callback_query_handler(text = "delete_config")
async def delete_config (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    if USLUGI_DB.find_one({"telegram_id": call.from_user.id}) is not None:
        srv = USLUGI_DB.find_one({"telegram_id": call.from_user.id})["srv_id"]
        match srv:
            case "srv1_rus_1":
                data_old = (requests.get(url=srv1_rus_1_url, headers=HEADERS)).json()
                for gays in USLUGI_DB.find({"telegram_id": call.from_user.id}):
                    presharedkey_old = gays['preshared_key']
                    for i in data_old:
                        if i['preshared_key']  == presharedkey_old:
                            public_key = i["url_safe_public_key"]
                            requests.delete(url=f'{srv1_rus_1_url}{public_key}/', headers=HEADERS)
                            USLUGI_DB.delete_one({"telegram_id": call.from_user.id, "preshared_key": presharedkey_old})
                await bot.send_message(call.from_user.id, 'Аккаунт удален!')
    else:
        await bot.send_message(call.from_user.id, 'Аккаунт не найден!')