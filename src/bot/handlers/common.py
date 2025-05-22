# src/bot/handlers/common.py
import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from datetime import datetime

from ..db import get_user, create_user, User as DBUser # Import DB functions and model
from ..ui.keyboards import mainMenu # Import keyboards

router = Router(name="common-handlers")

@router.message(CommandStart())
async def handle_start(message: types.Message):
    logging.info(f"User {message.from_user.id} ({message.from_user.full_name}) started the bot.")
    await message.answer(
        'Добро пожаловать в панель управления VPN аккаунтом',
        reply_markup=mainMenu
    )

    db_user = await get_user(message.from_user.id)
    if db_user is None:
        logging.info(f"New user: {message.from_user.id}. Creating database entry.")
        new_user_data = DBUser(
            telegram_id=message.from_user.id,
            tg_link=message.from_user.username, # Use .username for the link
            tg_name=message.from_user.full_name,
            tarif=None,
            tarif_exp=None,
            registration_date=datetime.now(), # Use datetime object
            test_active=True, # As per original logic (might need adjustment based on actual flow)
        )
        await create_user(new_user_data)
        logging.info(f"User {message.from_user.id} added to database.")
    else:
        logging.info(f"User {message.from_user.id} already exists.")
