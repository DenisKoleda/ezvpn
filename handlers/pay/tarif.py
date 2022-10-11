from main import dp, bot, YOOTOKEN, USERS_DB
from aiogram.types.message import ContentType
from datetime import timedelta, date, datetime
from aiogram import Bot , Dispatcher , executor , types
from handlers.keyboard import markups as nav

@dp.callback_query_handler(text = "tarif1")
async def tarif1 (call: types.CallbackQuery):
    await bot.delete_message (call.from_user.id, call.message.message_id)
    await bot.send_invoice (chat_id = call.from_user.id , title = "Оформление подписки", description = "Тестовое описание товара", payload="tarif1", provider_token=YOOTOKEN, currency="RUB", start_parameter="test_bot", prices=[{"label": "Руб", "amount": 30000}] )

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message : types.Message):
    match message.successful_payment.invoice_payload:
        case "tarif1":
            USERS_DB.update_one({"telegram_id": message.from_user.id}, {"$set": {"tarif": "Уверенная соточка", "tarif_exp": str(((date.today() + timedelta(days=30))))}})
            await bot.send_message(message.from_user.id, 'Подписка "Уверенная соточка" оформленна!')
        case "resume_tarif":
            USERS_DB.update_one({"telegram_id": message.from_user.id}, {"$set": { "tarif_exp": str(((datetime.strptime(USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif_exp'], "%Y-%m-%d").date()) + (timedelta(days=30))))}})
            await bot.send_message(message.from_user.id, f'Подписка продлена!\n\nВаш тариф: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif"]} \nВаша подписка истечет: {USERS_DB.find_one({"telegram_id": message.from_user.id})["tarif_exp"]}')

@dp.callback_query_handler(text = "resume_tarif")
async def resume_tarif (call: types.CallbackQuery):
    tarif = USERS_DB.find_one({"telegram_id": call.from_user.id})['tarif']
    match tarif:
        case "Уверенная соточка":
            await bot.send_invoice (chat_id = call.from_user.id , title = "Оформление подписки", description = "Тестовое описание товара", payload="resume_tarif", provider_token=YOOTOKEN, currency="RUB", start_parameter="test_bot", prices=[{"label": "Руб", "amount": 30000}] )