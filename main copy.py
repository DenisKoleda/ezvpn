import logging
from urllib import response
from aiogram import Bot , Dispatcher , executor , types
from aiogram.types.message import ContentType
import markups as nav
import requests
import asyncio
import pymongo
from datetime import timedelta, date
import wgconfig.wgexec as wgexec
import random
from test import test

URL = 'http://5.44.40.194:8000/v1/devices/wg0/peers/'
HEADERS = {'Authorization': 'Bearer secret',}
TOKEN = "5442137225:AAGvSu38dEXCDew52BWZZjyJIFm5HmDqdcA"
YOOTOKEN = "381764678:TEST:42654"
DB = pymongo.MongoClient("mongodb://localhost:27017/?retryWrites=true&w=majority")
USERS_DB = DB.vpn.users
USLUGI_DB = DB.vpn.uslugi

logging.basicConfig (level = logging.INFO)
#Initialize bot
bot = Bot (token = TOKEN)
dp = Dispatcher(bot)

async def vps_update():
    while True:
        today_date = date.today().strftime("%d/%m/%Y")
        for gays in USERS_DB.find({"tarif_exp": today_date}):
            await bot.send_message(gays['telegram_id'], f'У вас закончилась подписка: "{gays["tarif"]}"')
            USERS_DB.update_one({"telegram_id": gays['telegram_id']}, {"$set": {"tarif": None, "tarif_exp": None}})
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
            "registration_date": date.today().strftime("%d/%m/%Y"),
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
                    await bot.send_message(message.from_user.id, f'Ваш тариф: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif"]} \nВаша подписка истечет: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif_exp"]}')
                else:
                    await bot.send_message(message.from_user.id, f'У вас нет подписки :(')
            case 'УПРАВЛЕНИЕ ТАРИФОМ':
                if USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif'] is None :
                    await bot.send_message(message.from_user.id, f'У вас нет подписки :(')
                else:
                    await bot.send_message(message.from_user.id, f'Выберите сервер для создания аккаунта.\n\nВы можете переключаться между серверами в любой момент, но учитывайте что активный аккаунт у тарифа может быть один', reply_markup=nav.srv1_kb)
            case 'ТЕХ.ПОДДЕРЖКА':
                await bot.send_message(message.from_user.id, 'Чат тех.поддержки: vk.com')
            case 'ИНСТРУКЦИЯ':
                await bot.send_message(message.from_user.id, 'Инструции по настройке VPN в операционных системах', reply_markup = nav.bnt_intsr_Menu)
            case 'ГЛАВНОЕ МЕНЮ':
                await bot.send_message(message.from_user.id, 'Панель управления VPN аккаунтом', reply_markup = nav.mainMenu)


@dp.callback_query_handler(text = "submonth")
async def submonth (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_invoice (chat_id = call.from_user.id , title = "Оформление подписки", description = "Тестовое описание товара", payload="mouth_sub", provider_token=YOOTOKEN, currency="RUB", start_parameter="test_bot", prices=[{"label": "Руб", "amount": 30000}] )

@dp.callback_query_handler(text = "srv1_rus_1")
async def srv1_rus_1 (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_message (chat_id = call.from_user.id, text = 'Сервер "Россия #1"', reply_markup=nav.srv1_rus_1_kb)

@dp.callback_query_handler(text = "add_srv1_rus_1")
async def add_srv1_rus_1 (call: types.CallbackQuery):
    n = 1
    while True:
        presharedkey = wgexec.generate_presharedkey()
        ipv4 = random.randint(1, 254)
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
                print (gays)
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
            await bot.send_message(chat_id = call.from_user.id, text = "Аккаунт создан!")
            break
        else:
            print (f"Конфликт выдачи аккаунта, попытка решения {n}")
            n += 1
            await asyncio.sleep(1)
            if n == 10:
                await bot.send_message(chat_id = call.from_user.id, text = f'Ошибка выдачи доступа, пожалуйста обратитесь в тех.поддержку\n\nСообщите свой ID агенту тех.поддержки: {call.from_user.id}')
                break

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message : types.Message):
    match message.successful_payment.invoice_payload:
        case "mouth_sub":
            # Подписываем пользователя
            USERS_DB.update_one({"telegram_id": message.from_user.id}, {"$set": {"tarif": "Уверенная соточка", "tarif_exp": ((date.today() + timedelta(days=30)).strftime("%d/%m/%Y"))}})
            await bot.send_message(message.from_user.id, "Подписка 'Уверенная соточка' оформленна!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(vps_update())
    #add_srv1_rus_1.setup(dp)
    executor.start_polling(dp, skip_updates = True)