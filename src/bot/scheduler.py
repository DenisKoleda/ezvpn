# src/bot/scheduler.py
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .db import get_expired_users, update_user_tariff, get_all_user_services, delete_user_service
from .services.vpn_api import get_all_peers as vpn_get_all_peers, delete_peer as vpn_delete_peer
from .config import settings # To potentially get bot instance or send messages

# Placeholder for bot instance if needed for sending messages directly
# This will be passed from main app.py or set up via context
_bot_instance = None

def set_bot_instance(bot):
    global _bot_instance
    _bot_instance = bot

async def vps_update_task():
    logging.info("Running vps_update_task...")
    today = datetime.now() # Use datetime objects
    
    expired_db_users = await get_expired_users(today) # Expects datetime
    if not expired_db_users:
        logging.info("No users with expired tariffs found.")
        # return # Keep commented for now to test API interaction if needed

    # It's important to get the current state from the VPN server
    # The old code iterated through DB users, then for each user, iterated through their DB services,
    # then fetched ALL peers from VPN server, then matched. This is inefficient.
    # A better approach:
    # 1. Get all active peers from VPN server.
    # 2. For each expired user in DB:
    #    a. Get their services from DB.
    #    b. For each service, if its preshared_key matches a peer on the server, delete it.
    #    c. Update user's tariff in DB.
    #    d. Send notification.

    current_vpn_peers = await vpn_get_all_peers()
    if current_vpn_peers is None: # Check if API call failed
        logging.error("VPS Update Task: Failed to fetch current peers from VPN server.")
        return

    # Create a mapping of preshared_key to url_safe_public_key for efficient lookup
    vpn_peer_map = {peer.get('preshared_key'): peer.get('url_safe_public_key') for peer in current_vpn_peers if peer.get('preshared_key') and peer.get('url_safe_public_key')}

    for user in expired_db_users:
        logging.info(f"Processing expired user: {user.telegram_id}, Tarif: {user.tarif}, Expires: {user.tarif_exp}")
        
        user_services_in_db = await get_all_user_services(user.telegram_id)
        deleted_on_server_count = 0

        for service in user_services_in_db:
            if service.preshared_key in vpn_peer_map:
                url_safe_public_key = vpn_peer_map[service.preshared_key]
                logging.info(f"Attempting to delete VPN peer {url_safe_public_key} for user {user.telegram_id} (preshared_key: {service.preshared_key})")
                if await vpn_delete_peer(url_safe_public_key):
                    logging.info(f"Successfully deleted VPN peer {url_safe_public_key} from server.")
                    deleted_on_server_count += 1
                else:
                    logging.warning(f"Failed to delete VPN peer {url_safe_public_key} from server.")
            
            # Regardless of server deletion success, remove from our DB as it's expired
            await delete_user_service(user.telegram_id, service.preshared_key)
            logging.info(f"Deleted service record (preshared_key: {service.preshared_key}) from DB for user {user.telegram_id}")

        # Update user's tariff to None after processing all their services
        await update_user_tariff(user.telegram_id, tarif=None, tarif_exp=None)
        logging.info(f"Updated user {user.telegram_id} tariff to None in DB.")

        if _bot_instance:
            try:
                # Ensure tarif name is available for the message
                expired_tarif_name = user.tarif if user.tarif else "Unknown"
                await _bot_instance.send_message(user.telegram_id, f'У вас закончилась подписка: "{expired_tarif_name}"')
                logging.info(f"Sent subscription expiry notification to user {user.telegram_id}.")
            except Exception as e:
                logging.error(f"Failed to send message to user {user.telegram_id}: {e}")
        else:
            logging.warning("Bot instance not set in scheduler, cannot send expiry messages.")
    logging.info("vps_update_task finished.")


scheduler = AsyncIOScheduler(timezone="Europe/Moscow") # Or your desired timezone
# Schedule to run every 4 hours, similar to original `asyncio.sleep(14400)`
scheduler.add_job(vps_update_task, 'interval', hours=4, misfire_grace_time=60)
# For testing, you might want to run it more frequently, e.g., every 1 minute:
# scheduler.add_job(vps_update_task, 'interval', minutes=1)
