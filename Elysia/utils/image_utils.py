from typing import Optional
from Elysia.utils import requests


async def image_url2byte(url:str) -> Optional[bytes]:
    r = await requests.get(url)
    images_bytes = r.read()
    return images_bytes