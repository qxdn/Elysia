import httpx
from pydantic import BaseModel, Extra
from nonebot import get_driver
from nonebot.log import logger


class Config(BaseModel, extra=Extra.ignore):
    proxy: str


config: Config = Config.parse_obj(get_driver().config)

DEFAULT_TIMEOUT: int = 114514

if not config.proxy:
    proxy = dict()
else:
    proxy = {"all://": config.proxy}


async def post(url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs):
    logger.debug(f"POST {url} by {proxy if proxy else 'No Proxy'} with \n: {kwargs}")
    async with httpx.AsyncClient(proxies=proxy, timeout=timeout) as client:
        return await client.post(url, **kwargs)


async def get(url: str, timeout: int = DEFAULT_TIMEOUT, **kwargs):
    logger.debug(f"GET {url} by {proxy if proxy else 'No Proxy'} with \n: {kwargs}")
    async with httpx.AsyncClient(proxies=proxy, timeout=timeout) as client:
        return await client.get(url, **kwargs)
