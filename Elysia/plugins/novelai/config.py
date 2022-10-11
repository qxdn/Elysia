from pydantic import BaseSettings
from nonebot import get_driver


class Config(BaseSettings):
    # Your Config Here

    novelai_token: str

    class Config:
        extra = "ignore"


global_config = get_driver().config
config = Config.parse_obj(global_config)

header = {
    "authorization": "Bearer " + config.novelai_token,
    "content-type": "application/json",
    "referer": "https://ai.nya.la/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
}


baseTag="masterpiece, best quality,{{masterpiece}},extremely detailed,{best quality},{highres},original,[an extremely delicate and beatuiful]"
lowQuality = 'lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,'