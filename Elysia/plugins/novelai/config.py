from pydantic import BaseSettings
from nonebot import get_driver

from Elysia.plugins import novelai


class Config(BaseSettings):
    # Your Config Here

    novelai_token: str
    cloudserverapi_cookie:str

    class Config:
        extra = "ignore"


global_config = get_driver().config
config = Config.parse_obj(global_config)

novelai_header = {
    "authorization": "Bearer " + config.novelai_token,
    "content-type": "application/json",
    "referer": "https://ai.nya.la/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
}

cloudserverapi_header = {
    "authorization": "Bearer",
    "origin": "https://cloudserverapi.com",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "cookie": "cf_clearance=5iPFNFK9LeGPZMgbJB0cLIVuQB7A0RXLzbtpfHJeo4A-1665644673-0-150; __cf_bm=VL89VXuvhPWBYiwsYvBolhAnOtc8rxfNB87pfRABQ6U-1665644674-0-AQgH0Eqq7fbHDwuhTq8vTgqycJl9vtW6EgmN9lXsIJOzM6km48bs0WpbUK6RkppIZpGJbAk+bmGKPq32P/Bdvezv/6hChslOM6Jsr2+I8BBY4Zeaq6PY4uVw1lglm10f8A==; cf_use_ob=0",
}



baseTag="masterpiece, best quality,{{masterpiece}},extremely detailed,{best quality},{highres},"
lowQuality = 'lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,'