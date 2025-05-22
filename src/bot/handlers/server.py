# src/bot/handlers/server.py
import logging
import random
import asyncio # For sleep in add_srv1_rus_1
import os # For file operations if strictly needed, but prefer BufferedInputFile

from aiogram import Router, types, F, Bot
from aiogram.types import BufferedInputFile # For sending files

# VPN Key Generation (assuming wgconfig is available)
try:
    import wgconfig.wgexec as wgexec
    WGEXEC_AVAILABLE = True
except ImportError:
    logging.warning("wgconfig.wgexec not found. VPN key generation will be disabled.")
    WGEXEC_AVAILABLE = False

from ..db import (
    get_user, get_user_service, get_all_user_services, create_service, delete_user_service,
    find_service_by_ip, find_service_by_key, User as DBUser, Service as DBService
)
from ..services.vpn_api import (
    get_all_peers as vpn_get_all_peers,
    create_peer as vpn_create_peer,
    delete_peer as vpn_delete_peer,
    get_peer_config_file,
    get_peer_config_png
)
from ..ui.keyboards import srv1_kb, srv1_rus_1_kb #, mainMenu (if needed for exit)
from ..config import settings # For any server-specific settings if not already in vpn_api

router = Router(name="server-management-handlers")

# Callback for "srv1_list" (Show server list - e.g., from "УПРАВЛЕНИЕ ТАРИФОМ" -> back button)
@router.callback_query(F.data == "srv1_list")
async def handle_show_server_list(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} requested server list (srv1_list).")
    await callback_query.message.edit_text( # Edit existing message
        'Доступные серверы:',
        reply_markup=srv1_kb
    )
    await callback_query.answer()

# Callback for "srv1_rus_1" (Show specific server info)
@router.callback_query(F.data == "srv1_rus_1")
async def handle_show_srv1_rus_1_info(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} requested info for srv1_rus_1.")
    await callback_query.message.edit_text( # Edit existing message
        'Сервер "Россия #1"\n\nСамый быстрый и топ сервер, а то', # Text from original
        reply_markup=srv1_rus_1_kb # Keyboard with "Создать аккаунт", "Назад"
    )
    await callback_query.answer()

# Callback for "srv_exit" (Exit server menu - typically deletes the message)
@router.callback_query(F.data == "srv_exit")
async def handle_server_menu_exit(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} exited server menu (srv_exit).")
    await callback_query.message.delete()
    await callback_query.answer("Меню закрыто.")

# Callback for "srv1_to_srv2" (Placeholder for next page of servers)
@router.callback_query(F.data == "srv1_to_srv2")
async def handle_server_page_next(callback_query: types.CallbackQuery, bot: Bot):
    logging.info(f"User {callback_query.from_user.id} requested next server page (srv1_to_srv2).")
    await callback_query.answer("Пока нету (Страница 2)", show_alert=True) # Original text "Пока нету ("

# Callback for "add_srv1_rus_1" (Create VPN account on server Russia #1)
@router.callback_query(F.data == "add_srv1_rus_1")
async def handle_add_srv1_rus_1(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    logging.info(f"User {user_id} attempting to add VPN config for srv1_rus_1.")

    if not WGEXEC_AVAILABLE:
        await callback_query.answer("Ошибка: Генерация ключей VPN недоступна.", show_alert=True)
        return

    # Check if user has an active tariff (important prerequisite)
    user_db_info = await get_user(user_id)
    if not user_db_info or not user_db_info.tarif:
        await callback_query.answer("У вас нет активной подписки для создания VPN конфигурации.", show_alert=True)
        return

    await callback_query.answer("Начинаем создание аккаунта...") # Initial feedback

    try:
        await callback_query.message.delete()
    except Exception as e:
        logging.warning(f"Could not delete message for user {user_id} during add_srv1_rus_1: {e}")

    existing_services_for_user = await get_all_user_services(user_id)
    vpn_peers_on_server = await vpn_get_all_peers() 

    if vpn_peers_on_server is None:
        await bot.send_message(user_id, "Не удалось связаться с VPN сервером. Попробуйте позже.")
        return

    vpn_peer_map = {peer.get('preshared_key'): peer.get('url_safe_public_key') for peer in vpn_peers_on_server if peer.get('preshared_key')}

    for service_in_db in existing_services_for_user:
        if service_in_db.preshared_key in vpn_peer_map:
            logging.info(f"User {user_id} has existing config {service_in_db.preshared_key} on server. Deleting it.")
            await vpn_delete_peer(vpn_peer_map[service_in_db.preshared_key])
        await delete_user_service(user_id, service_in_db.preshared_key) 

    max_retries = 10
    for attempt in range(max_retries):
        presharedkey = wgexec.generate_presharedkey()
        random_octet = random.randint(2, 254) 
        generated_ip = f'10.10.1.{random_octet}/32'
        
        ip_conflict = await find_service_by_ip(generated_ip) 
        key_conflict = await find_service_by_key(presharedkey)
        
        if not ip_conflict and not key_conflict:
            logging.info(f"Attempt {attempt+1}: Generated unique IP {generated_ip} and PSK {presharedkey} for user {user_id}.")
            
            api_response = await vpn_create_peer(allowed_ips=[generated_ip], preshared_key=presharedkey)
            
            if api_response: 
                new_service = DBService(
                    telegram_id=user_id,
                    tarif_ip=generated_ip,
                    preshared_key=presharedkey,
                    srv_id="srv1_rus_1" 
                )
                await create_service(new_service)
                logging.info(f"VPN config for user {user_id} created successfully on server and DB.")
                await bot.send_message(user_id, 'Аккаунт создан!\nЗайдите в "МОЙ ТАРИФ", чтобы скачать конфигурацию.')
                return 
            else:
                logging.error(f"Failed to create peer on VPN server for user {user_id} with IP {generated_ip}.")
        
        logging.warning(f"Attempt {attempt+1} for user {user_id}: Conflict found or API error. IP: {generated_ip}, Key Conflict: {bool(key_conflict)}, IP Conflict: {bool(ip_conflict)}. Retrying...")
        await asyncio.sleep(1)

    logging.error(f"Failed to create VPN config for user {user_id} after {max_retries} attempts.")
    await bot.send_message(user_id, f'Ошибка выдачи доступа, пожалуйста обратитесь в тех.поддержку\n\nСообщите свой ID агенту тех.поддержки: {user_id}')

# Callback for "download_config"
@router.callback_query(F.data == "download_config")
async def handle_download_config(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    logging.info(f"User {user_id} requested to download config.")
    await callback_query.answer("Получаем конфигурацию...")

    user_service = await get_user_service(user_id) 

    if not user_service or user_service.srv_id != "srv1_rus_1": 
        await callback_query.message.answer("Активная конфигурация для этого сервера не найдена.")
        return

    vpn_peers = await vpn_get_all_peers()
    if vpn_peers is None:
        await callback_query.message.answer("Ошибка: Не удалось связаться с VPN сервером.")
        return

    url_safe_public_key = None
    for peer in vpn_peers:
        if peer.get('preshared_key') == user_service.preshared_key:
            url_safe_public_key = peer.get('url_safe_public_key')
            break
    
    if not url_safe_public_key:
        await callback_query.message.answer("Ошибка: Не удалось найти вашу конфигурацию на VPN сервере.")
        logging.error(f"Config for psk {user_service.preshared_key} user {user_id} not found on VPN server peer list.")
        return

    conf_file_content = await get_peer_config_file(url_safe_public_key)
    if conf_file_content:
        conf_file_bytes = conf_file_content.encode('utf-8')
        input_file_conf = BufferedInputFile(conf_file_bytes, filename=f"{user_id}_{user_service.srv_id}.conf")
        await bot.send_document(user_id, document=input_file_conf)
    else:
        await bot.send_message(user_id, "Не удалось получить файл конфигурации (.conf).")

    qr_code_bytes = await get_peer_config_png(url_safe_public_key, params={'width': '256'})
    if qr_code_bytes:
        input_file_png = BufferedInputFile(qr_code_bytes, filename=f"{user_id}_{user_service.srv_id}.png")
        await bot.send_photo(user_id, photo=input_file_png)
    else:
        await bot.send_message(user_id, "Не удалось получить QR-код конфигурации (.png).")
    
    if conf_file_content or qr_code_bytes:
            await bot.send_message(user_id, "Ваши данные для подключения!")
    else:
        await bot.send_message(user_id, "Не удалось получить файлы конфигурации. Обратитесь в поддержку.")
    
    try:
        await callback_query.message.delete()
    except Exception as e:
        logging.warning(f"Could not delete message for user {user_id} during download_config: {e}")

# Callback for "delete_config"
@router.callback_query(F.data == "delete_config")
async def handle_delete_config(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    logging.info(f"User {user_id} requested to delete config.")
    await callback_query.answer("Удаляем конфигурацию...")

    user_services = await get_all_user_services(user_id) 
    if not user_services:
        await callback_query.message.answer("У вас нет активных конфигураций для удаления.")
        return

    deleted_count_db = 0
    deleted_count_api = 0

    vpn_peers = await vpn_get_all_peers() 
    if vpn_peers is None:
        await callback_query.message.answer("Ошибка: Не удалось связаться с VPN сервером для удаления.")
        return
    
    vpn_peer_map_by_psk = {peer.get('preshared_key'): peer.get('url_safe_public_key') for peer in vpn_peers if peer.get('preshared_key')}

    for service_to_delete in user_services:
        if service_to_delete.srv_id == "srv1_rus_1": 
            public_key_to_delete = vpn_peer_map_by_psk.get(service_to_delete.preshared_key)
            if public_key_to_delete:
                if await vpn_delete_peer(public_key_to_delete):
                    logging.info(f"Successfully deleted VPN peer {public_key_to_delete} from server for user {user_id}.")
                    deleted_count_api +=1
                else:
                    logging.warning(f"Failed to delete VPN peer {public_key_to_delete} from server for user {user_id}.")
            else:
                logging.warning(f"Preshared key {service_to_delete.preshared_key} for user {user_id} not found on VPN server during delete.")
            
            await delete_user_service(user_id, service_to_delete.preshared_key)
            logging.info(f"Deleted service record (preshared_key: {service_to_delete.preshared_key}) from DB for user {user_id}")
            deleted_count_db +=1
    
    if deleted_count_db > 0:
        await bot.send_message(user_id, f"Удалено конфигураций: {deleted_count_db}.")
    else:
        await bot.send_message(user_id, "Не найдено активных конфигураций для удаления на этом сервере.")

    try:
        await callback_query.message.delete()
    except Exception as e:
        logging.warning(f"Could not delete message for user {user_id} during delete_config: {e}")
