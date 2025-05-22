# src/bot/handlers/menu.py
import logging
from aiogram import Router, types, F
from datetime import datetime # For potential use, though not directly in these handlers

from ..db import get_user # User model for type hinting if needed, or specific fields
from ..ui.keyboards import sub_inline_markup, mainMenu, bnt_usr_main, srv1_kb, bnt_intsr_Menu

router = Router(name="menu-handlers")

# Handler for 'КУПИТЬ VPN'
@router.message(F.text.lower() == 'купить vpn') # Using F.text for robust matching
async def handle_buy_vpn(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'КУПИТЬ VPN'")
    user = await get_user(message.from_user.id) # Fetches the Pydantic User model instance
    
    if user and user.tarif is not None:
        await message.answer(
            'Обнаружили у вас действующую подписку!!! \n'
            'При покупке новой подписки старая автоматически удалится!!!\n\n'
            'Если вам требуется продлить услугу, то зайдите в "МОЙ ТАРИФ"'
        )
    await message.answer('Доступные тарифы:', reply_markup=sub_inline_markup)

# Handler for 'МОЙ ТАРИФ'
@router.message(F.text.lower() == 'мой тариф')
async def handle_my_tariff(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'МОЙ ТАРИФ'")
    user = await get_user(message.from_user.id)
    if user and user.tarif is not None:
        # Ensure tarif_exp is formatted if it's a datetime object
        tarif_exp_str = user.tarif_exp.strftime("%d/%m/%Y") if user.tarif_exp else "не указана"
        await message.answer(
            f'Ваш тариф: {user.tarif} \n'
            f'Ваша подписка истечет: {tarif_exp_str}',
            reply_markup=bnt_usr_main # Keyboard for managing tariff
        )
    else:
        await message.answer('У вас нет подписки :(')

# Handler for 'УПРАВЛЕНИЕ ТАРИФОМ'
@router.message(F.text.lower() == 'управление тарифом')
async def handle_manage_tariff(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'УПРАВЛЕНИЕ ТАРИФОМ'")
    user = await get_user(message.from_user.id)
    # The original logic for this part was:
    # if USERS_DB.find_one({"telegram_id": message.from_user.id})['tarif'] is None :
    #    await bot.send_message(message.from_user.id, 'У вас нет подписки :(')
    # else:
    #    await bot.send_message(message.from_user.id, 'Выберите сервер для создания аккаунта....', reply_markup=srv1_kb)
    # This means if 'tarif' field IS None, they get "no subscription". Otherwise, they get server list.
    if user and user.tarif is None: # This matches the original logic
        await message.answer('У вас нет подписки :(')
    elif user and user.tarif is not None: # User has a tarif
        await message.answer(
            'Выберите сервер для создания аккаунта.\n'
            'Вы можете переключаться между серверами в любой момент, '
            'но учитывайте что активный аккаунт у тарифа может быть один.\n\n'
            'Доступные серверы:',
            reply_markup=srv1_kb # Keyboard for server list
        )
    else: # User not found in DB at all, which implies no subscription
        await message.answer('У вас нет подписки :(')


# Handler for 'ТЕХ.ПОДДЕРЖКА'
@router.message(F.text.lower() == 'тех.поддержка')
async def handle_support(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'ТЕХ.ПОДДЕРЖКА'")
    await message.answer('Чат тех.поддержки: vk.com') # Placeholder URL from original

# Handler for 'ИНСТРУКЦИЯ'
@router.message(F.text.lower() == 'инструкция')
async def handle_instructions(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'ИНСТРУКЦИЯ'")
    await message.answer('Инструкции по настройке VPN в операционных системах', reply_markup=bnt_intsr_Menu)

# Handler for 'ГЛАВНОЕ МЕНЮ'
@router.message(F.text.lower() == 'главное меню')
async def handle_main_menu_redirect(message: types.Message):
    logging.info(f"User {message.from_user.id} selected 'ГЛАВНОЕ МЕНЮ'")
    await message.answer('Панель управления VPN аккаунтом', reply_markup=mainMenu)
