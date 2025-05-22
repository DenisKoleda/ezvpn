from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[object] = Field(default=None, alias="_id") # For MongoDB's _id
    telegram_id: int
    tg_link: Optional[str] = None
    tg_name: Optional[str] = None
    tarif: Optional[str] = None
    tarif_exp: Optional[datetime] = None
    registration_date: datetime
    test_active: bool = False

    class Config:
        populate_by_name = True # Allows using "_id" field name for "id"
        json_encoders = {
            datetime: lambda dt: dt.isoformat(), # How to serialize datetime to JSON
            object: lambda o: str(o) # How to serialize ObjectId to JSON
        }


class Service(BaseModel):
    id: Optional[object] = Field(default=None, alias="_id") # For MongoDB's _id
    telegram_id: int
    tarif_ip: Optional[str] = None # e.g., '10.10.1.X/32'
    preshared_key: str
    srv_id: str # e.g., "srv1_rus_1"

    class Config:
        populate_by_name = True
        json_encoders = {object: lambda o: str(o)}
