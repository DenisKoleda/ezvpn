from aiogram import Bot , Dispatcher , executor , types
from aiogram.types.message import ContentType
from handlers.keyboard import markups as nav
from main import dp, bot

HEADERS = {'Authorization': 'Bearer secret',}
srv1_rus_1_url = 'http://5.44.40.194:8000/v1/devices/wg0/peers/'

@dp.callback_query_handler(text = "srv1_list")
async def srv1_rus_1 (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_message (chat_id = call.from_user.id, text = 'Доступные серверы:', reply_markup=nav.srv1_kb)

@dp.callback_query_handler(text = "srv1_rus_1")
async def srv1_rus_1 (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_message (chat_id = call.from_user.id, text = 'Сервер "Россия #1"\n\nСамый быстрый и топ сервер, а то', reply_markup=nav.srv1_rus_1_kb)

@dp.callback_query_handler(text = "srv_exit")
async def srv_exit (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)

@dp.callback_query_handler(text = "srv1_to_srv2")
async def srv1_to_srv2 (call: types.CallbackQuery):
    #await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_message (chat_id = call.from_user.id, text = 'Пока нету (')
