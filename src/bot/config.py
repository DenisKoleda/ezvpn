from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, SecretStr, Field
from typing import Dict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    bot_token: SecretStr
    db_url: str = "mongodb://localhost:27017/"
    db_name: str = "vpn"
    yoo_token: SecretStr

    vpn_api_url_srv1_rus_1: AnyHttpUrl = "http://5.44.40.194:8000/v1/devices/wg0/peers/"
    # Store headers as a JSON string in .env, then parse here if complex, or keep simple like this
    # For simplicity, we'll assume a structure that can be directly used or slightly processed.
    # If headers are static and simple, they can be defined directly.
    # For this iteration, let's assume it's a simple, fixed header.
    # More complex scenarios might involve parsing from a JSON string in the .env.
    vpn_api_headers: Dict[str, str] = Field(default_factory=lambda: {'Authorization': 'Bearer secret'})


settings = Settings()
