import httpx
from typing import Optional, List, Dict, Any
from ..config import settings # Relative import from parent directory's config

# Using the specific server URL and headers from config
# If multiple servers are supported in the future, this module might need to be more dynamic
API_URL = str(settings.vpn_api_url_srv1_rus_1) # Ensure it's a string
API_HEADERS = settings.vpn_api_headers.copy() # Use a copy to avoid accidental modification if needed

async def get_all_peers() -> List[Dict[str, Any]]:
    """Fetches all peers from the VPN server."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL, headers=API_HEADERS)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while getting all peers: {e}")
            # Potentially re-raise or return a specific error object
            return [] # Or raise custom exception
        except httpx.RequestError as e:
            print(f"Request error occurred while getting all peers: {e}")
            return [] # Or raise custom exception

async def create_peer(allowed_ips: List[str], preshared_key: str) -> Optional[Dict[str, Any]]:
    """Creates a new peer on the VPN server."""
    data = {
        'allowed_ips': allowed_ips,
        'preshared_key': preshared_key,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, headers=API_HEADERS, json=data)
            response.raise_for_status()
            return response.json() # Assuming the API returns the created peer's data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while creating peer: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error occurred while creating peer: {e}")
            return None

async def delete_peer(url_safe_public_key: str) -> bool:
    """Deletes a peer from the VPN server using its URL-safe public key."""
    delete_url = f"{API_URL.rstrip('/')}/{url_safe_public_key}/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(delete_url, headers=API_HEADERS)
            response.raise_for_status()
            return True # Successfully deleted
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while deleting peer {url_safe_public_key}: {e}")
            return False
        except httpx.RequestError as e:
            print(f"Request error occurred while deleting peer {url_safe_public_key}: {e}")
            return False

async def get_peer_config_file(url_safe_public_key: str) -> Optional[str]:
    """Fetches the .conf file content for a specific peer."""
    config_url = f"{API_URL.rstrip('/')}/{url_safe_public_key}/quick.conf"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(config_url, headers=API_HEADERS)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching config file for {url_safe_public_key}: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error fetching config file for {url_safe_public_key}: {e}")
            return None

async def get_peer_config_png(url_safe_public_key: str, params: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
    """Fetches the QR code .png file content for a specific peer."""
    png_url = f"{API_URL.rstrip('/')}/{url_safe_public_key}/quick.conf.png"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(png_url, headers=API_HEADERS, params=params)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching PNG for {url_safe_public_key}: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error fetching PNG for {url_safe_public_key}: {e}")
            return None
