from motor.motor_asyncio import AsyncIOMotorClient
from ..config import settings
from .models import User, Service # Assuming models are in .models
from typing import Optional, List
from datetime import datetime

client = AsyncIOMotorClient(settings.db_url)
db = client[settings.db_name]
users_collection = db["users"]
uslugi_collection = db["uslugi"] # 'uslugi' seems to be the name for VPN configurations/services

# User operations
async def get_user(telegram_id: int) -> Optional[User]:
    user_data = await users_collection.find_one({"telegram_id": telegram_id})
    if user_data:
        return User(**user_data)
    return None

async def create_user(user: User) -> User:
    # Pydantic model will be converted to dict for MongoDB
    user_dict = user.model_dump(by_alias=True, exclude_none=True)
    await users_collection.insert_one(user_dict)
    # Note: MongoDB automatically adds _id, so user_dict will not have it unless re-fetched or handled
    return user # Or fetch and return with ID

async def update_user_tariff(telegram_id: int, tarif: Optional[str], tarif_exp: Optional[datetime]):
    update_data = {"$set": {"tarif": tarif, "tarif_exp": tarif_exp}}
    await users_collection.update_one({"telegram_id": telegram_id}, update_data)

async def get_expired_users(today_date: datetime) -> List[User]:
    # In MongoDB, for date-only comparisons, ensure times are handled or use date range queries.
    # If tarif_exp stores just date, comparison should be against date.
    # For this example, assuming tarif_exp can be compared directly.
    # The original code used string dates: str(date.today()).
    # We are now using datetime. This query will need adjustment based on how dates are stored.
    # If storing as datetime, but only care about date part:
    # query = {"tarif_exp": {"$lt": today_date_midnight_next_day, "$gte": today_date_midnight_this_day}}
    # For simplicity now, let's assume a direct comparison is okay, will refine in vps_update refactor
    cursor = users_collection.find({"tarif_exp": {"$lt": today_date}})
    expired_users = []
    for doc in await cursor.to_list(length=None):
        expired_users.append(User(**doc))
    return expired_users


# Service/VPN Config operations
async def get_user_service(telegram_id: int, srv_id: Optional[str] = None) -> Optional[Service]:
    query = {"telegram_id": telegram_id}
    if srv_id:
        query["srv_id"] = srv_id
    service_data = await uslugi_collection.find_one(query)
    if service_data:
        return Service(**service_data)
    return None

async def get_all_user_services(telegram_id: int) -> List[Service]:
    cursor = uslugi_collection.find({"telegram_id": telegram_id})
    services = []
    for doc in await cursor.to_list(length=None):
        services.append(Service(**doc))
    return services

async def create_service(service: Service) -> Service:
    service_dict = service.model_dump(by_alias=True, exclude_none=True)
    await uslugi_collection.insert_one(service_dict)
    return service

async def delete_user_service(telegram_id: int, preshared_key: str):
    await uslugi_collection.delete_one({"telegram_id": telegram_id, "preshared_key": preshared_key})

async def delete_all_user_services(telegram_id: int):
    await uslugi_collection.delete_many({"telegram_id": telegram_id})
    
async def find_service_by_ip(ip: str) -> Optional[Service]:
    service_data = await uslugi_collection.find_one({"tarif_ip": ip})
    if service_data:
        return Service(**service_data)
    return None

async def find_service_by_key(preshared_key: str) -> Optional[Service]:
    service_data = await uslugi_collection.find_one({"preshared_key": preshared_key})
    if service_data:
        return Service(**service_data)
    return None
