from random import choice
from nonebot import get_driver
from nonebot.adapters.onebot.v11.helpers import Cooldown,extract_image_urls
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from .data_source import SauceNAO
from .config import Config

_search_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])

plugin_config: Config = Config.parse_obj(get_driver().config)


saucenao = SauceNAO(api_key=plugin_config.saucenao_api)

saucenao_matcher = saucenao.on_message("搜图","通过图片反向查询出处")

@saucenao_matcher.handle([Cooldown(5, prompt=_search_flmt_notice)])
async def _deal_search(event: MessageEvent):

    user_id = event.get_user_id()
    img = extract_image_urls(event.message)
    if not img:
        await saucenao_matcher.reject("请发送图片而不是其他东西！！")
    # TODO: 消息处理
    r,_ = await saucenao.search_from_url(img[0])
    
    result = f"> {MessageSegment.at(user_id)}" +  f"{MessageSegment.image(r[0].thumbnail)}"
    await saucenao_matcher.finish(Message(result))