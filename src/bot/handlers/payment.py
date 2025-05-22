# src/bot/handlers/payment.py
import logging
from aiogram import Router, types, F, Bot
from aiogram.types.message import ContentType
from datetime import datetime, timedelta

from ..db import get_user, update_user_tariff, User as DBUser
from ..config import settings
# Assuming sub_inline_markup might be used if payment is re-initiated from some menu
# from ..ui.keyboards import sub_inline_markup 

router = Router(name="payment-handlers")

# Callback for 'tarif1' (e.g., "Уверенная соточка - 300 рублей")
# This was originally in handlers/pay/tarif.py
@router.callback_query(F.data == "tarif1")
async def handle_tarif1_payment_init(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} initiated payment for 'tarif1'")
    await callback_query.message.delete() # Original behavior: delete the message with the button
    
    # Price is in minimal units (e.g., kopecks for RUB)
    # 30000 kopecks = 300 RUB
    prices = [types.LabeledPrice(label="Руб", amount=30000)] 
    
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="Оформление подписки",
        description="Подписка 'Уверенная соточка'", # More descriptive
        payload="tarif1_payload", # Unique payload for this specific tariff and action
        provider_token=settings.yoo_token.get_secret_value(),
        currency="RUB",
        prices=prices,
        start_parameter="one_month_sub_test_bot" # Deep-linking parameter
    )
    await callback_query.answer() # Important to answer callback queries

# Callback for 'resume_tarif'
# This was originally in handlers/pay/tarif.py
@router.callback_query(F.data == "resume_tarif")
async def handle_resume_tarif_payment_init(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} initiated payment to resume tariff.")
    user = await get_user(callback_query.from_user.id)
    
    if not user or not user.tarif:
        await callback_query.answer("Не найден активный тариф для продления.", show_alert=True)
        if callback_query.message: # try to delete message if it exists
             await callback_query.message.delete()
        return

    # Example: "Уверенная соточка" costs 300 RUB to resume
    # This might need to be more dynamic if different tariffs have different resume prices
    # For now, assuming the same price as tarif1
    payload_str = f"resume_tarif_payload:{user.tarif}" # Payload can carry info
    title_str = f"Продление подписки: {user.tarif}"
    prices = [types.LabeledPrice(label="Руб", amount=30000)] # 300 RUB

    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=title_str,
        description=f"Продление подписки {user.tarif} еще на 30 дней.",
        payload=payload_str,
        provider_token=settings.yoo_token.get_secret_value(),
        currency="RUB",
        prices=prices,
        start_parameter="resume_sub_test_bot"
    )
    await callback_query.answer()
    if callback_query.message: # try to delete message if it exists
        await callback_query.message.delete()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    logging.info(f"Processing pre-checkout query for {pre_checkout_query.from_user.id}, payload: {pre_checkout_query.invoice_payload}")
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    logging.info(f"Pre-checkout query for {pre_checkout_query.from_user.id} approved.")

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.SuccessfulPayment, bot: Bot):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    logging.info(f"Successful payment from {user_id}, payload: {payload}")

    new_tarif_name = None
    new_tarif_exp_date = None

    if payload == "tarif1_payload":
        new_tarif_name = "Уверенная соточка"
        # Set expiry 30 days from now
        new_tarif_exp_date = datetime.now() + timedelta(days=30)
        await update_user_tariff(user_id, tarif=new_tarif_name, tarif_exp=new_tarif_exp_date)
        await bot.send_message(user_id, f'Подписка "{new_tarif_name}" оформлена! Срок действия до: {new_tarif_exp_date.strftime("%d/%m/%Y")}')
    
    elif payload.startswith("resume_tarif_payload:"):
        # original_tarif_name = payload.split(":")[1] # If needed
        user = await get_user(user_id)
        if user and user.tarif_exp:
            # Extend from current expiry date
            new_tarif_exp_date = user.tarif_exp + timedelta(days=30)
        else:
            # If no previous expiry (should not happen for resume, but as fallback)
            new_tarif_exp_date = datetime.now() + timedelta(days=30)
        
        # Tarif name remains the same, only expiry changes
        await update_user_tariff(user_id, tarif=user.tarif, tarif_exp=new_tarif_exp_date) # Keep existing tarif name
        await bot.send_message(user_id, f'Подписка "{user.tarif}" продлена! Новый срок действия до: {new_tarif_exp_date.strftime("%d/%m/%Y")}')
    
    else:
        logging.warning(f"Unknown successful payment payload: {payload} from user {user_id}")
        await bot.send_message(user_id, "Платеж получен, но не удалось определить тип подписки. Обратитесь в поддержку.")

# Note: The `submonth` callback from `main copy.py` seems to be equivalent to `tarif1`.
# It also uses YOOTOKEN and payload "mouth_sub", amount 30000.
# The `process_pay` in `main copy.py` for "mouth_sub" is also similar.
# The refactored `tarif1_payload` and its handling cover this.
