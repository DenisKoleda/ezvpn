import logging
from urllib import response
from aiogram import Bot , Dispatcher , executor , types
from aiogram.types.message import ContentType
from handlers.keyboard import markups as nav
import requests
import asyncio
import pymongo
from datetime import timedelta, date
import wgconfig.wgexec as wgexec
import random


TOKEN = "5442137225:AAGvSu38dEXCDew52BWZZjyJIFm5HmDqdcA"
YOOTOKEN = "381764678:TEST:42654"
DB = pymongo.MongoClient("mongodb://localhost:27017/?retryWrites=true&w=majority")
USERS_DB = DB.vpn.users
USLUGI_DB = DB.vpn.uslugi

logging.basicConfig (level = logging.INFO)
#Initialize bot
bot = Bot (token = TOKEN)
dp = Dispatcher(bot)

HEADERS = {'Authorization': 'Bearer secret',}
srv1_rus_1_url = 'http://5.44.40.194:8000/v1/devices/wg0/peers/'

async def vps_update():
    while True:
        today_date = str(date.today())
        for gays in USERS_DB.find({"tarif_exp": today_date}):
            await bot.send_message(gays['telegram_id'], f'У вас закончилась подписка: "{gays["tarif"]}"')
            USERS_DB.update_one({"telegram_id": gays['telegram_id']}, {"$set": {"tarif": None, "tarif_exp": None}})
            if USLUGI_DB.find_one({"telegram_id": gays['telegram_id']}) is not None:
                srv = USLUGI_DB.find_one({"telegram_id": gays['telegram_id']})["srv_id"]
                match srv:
                    case "srv1_rus_1":
                        data_old = (requests.get(url=srv1_rus_1_url, headers=HEADERS)).json()
                        for gays in USLUGI_DB.find({"telegram_id": gays['telegram_id']}):
                            presharedkey_old = gays['preshared_key']
                            for i in data_old:
                                if i['preshared_key']  == presharedkey_old:
                                    public_key = i["url_safe_public_key"]
                                    requests.delete(url=f'{srv1_rus_1_url}{public_key}/', headers=HEADERS)
                                    USLUGI_DB.delete_one({"telegram_id": gays['telegram_id'], "preshared_key": presharedkey_old})
                        print(f'{gays["tg_name"]} {gays["telegram_id"]} истек срок')
        await asyncio.sleep(14400) # 4 Часа

@dp.message_handler(commands = ['start'])
async def start (message : types.Message ) :
    await bot.send_message(message.from_user.id ,'Добро пожаловать в панель управления VPN аккаунтом', reply_markup = nav.mainMenu )
    if USERS_DB.find_one({"telegram_id": message.from_user.id}) is None:
        post = {
            "telegram_id": message.from_user.id,
            "tg_link": message.from_user.username,
            "tg_name": message.from_user.full_name,
            "tarif": None,
            "tarif_exp": None,
            "registration_date": str(date.today()),
            "test_active": True,
        }
        USERS_DB.insert_one(post)

@dp.message_handler()
async def bot_message (message: types.Message) :
    if message.chat.type == 'private' :
        match message.text:
            case 'КУПИТЬ VPN':
                if USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif'] is not None :
                    await bot.send_message(message.from_user.id, 'Обнаружили у вас действующую подписку!!! \nПри покупке новой подписки старая автоматически удалится!!!\n\nЕсли вам требуется продлить услугу, то зайдите в "МОЙ ТАРИФ"')
                await bot.send_message(message.from_user.id, 'Доступные тарифы:', reply_markup = nav.sub_inline_markup)
            case 'МОЙ ТАРИФ':
                if USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif'] is not None :
                    await bot.send_message(message.from_user.id, f'Ваш тариф: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif"]} \nВаша подписка истечет: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif_exp"]}', reply_markup=nav.bnt_usr_main)
                else:
                    await bot.send_message(message.from_user.id, f'У вас нет подписки :(')
            case 'УПРАВЛЕНИЕ ТАРИФОМ':
                if USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif'] is None :
                    await bot.send_message(message.from_user.id, f'У вас нет подписки :(')
                else:
                    await bot.send_message(message.from_user.id, f'Выберите сервер для создания аккаунта.\nВы можете переключаться между серверами в любой момент, но учитывайте что активный аккаунт у тарифа может быть один.\n\nДоступные серверы:', reply_markup=nav.srv1_kb)
            case 'ТЕХ.ПОДДЕРЖКА':
                await bot.send_message(message.from_user.id, 'Чат тех.поддержки: vk.com')
            case 'ИНСТРУКЦИЯ':
                await bot.send_message(message.from_user.id, 'Инструции по настройке VPN в операционных системах', reply_markup = nav.bnt_intsr_Menu)
            case 'ГЛАВНОЕ МЕНЮ':
                await bot.send_message(message.from_user.id, 'Панель управления VPN аккаунтом', reply_markup = nav.mainMenu)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(vps_update())
    from handlers import dp
    executor.start_polling(dp, skip_updates = True)