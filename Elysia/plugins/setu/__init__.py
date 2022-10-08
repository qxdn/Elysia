from random import choice
from re import I
import json


from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Event,
    GroupMessageEvent,
    Message,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.utils import DataclassEncoder
from nonebot.typing import T_State
from nonebot.log import logger

from .config import Setu_Type
from .data_source import Setu

_search_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])

setu = Setu()
random_setu = setu.on_regex(
    "(来[张|个|份])?(.*?)(的)?([rR]18)?[色涩🐍瑟]图",
    "来张随机色图",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)


def _get_args(state: T_State):
    args = list(state["_matched_groups"])
    tags: str = args[1]
    r18: str = args[3]
    # 如果有标签
    if tags:
        # 用空格分割
        tags: str = tags.split(" ")

    if r18:
        r18 = Setu_Type.R18
    else:
        r18 = Setu_Type.NON_R18

    return r18, tags


def _generate_msg(info, url):
    msg = Message([MessageSegment.text(info), MessageSegment.image(url)])
    return msg


# 冷却30秒
@random_setu.handle([Cooldown(30, prompt=_search_flmt_notice)])
async def get_random_setu_private(bot: Bot, event: PrivateMessageEvent, state: T_State):

    r18, tags = _get_args(state)

    logger.debug(f"searching private setu params:\n r18:{r18},tags:{tags}")

    info, url = await Setu.random_setu(r18, tags)

    logger.debug(f"info:{info}")
    logger.debug(f"url:{url}")

    if None == url:
        await random_setu.finish("找不到呢")

    msg = _generate_msg(info, url)

    await random_setu.finish(msg)


# 冷却30
@random_setu.handle([Cooldown(30, prompt=_search_flmt_notice)])
async def get_random_setu_group(bot: Bot, event: GroupMessageEvent, state: T_State):
    r18, tags = _get_args(state)

    logger.debug(f"searching group setu params:\n r18:{r18},tags:{tags}")

    info, url = await Setu.random_setu(r18, tags)

    logger.debug(f"info:{info}")
    logger.debug(f"url:{url}")

    if None == url:
        await random_setu.finish("找不到呢")

    msg = _generate_msg(info, url)
    msg: dict = json.loads(json.dumps(msg, cls=DataclassEncoder))
    login = await bot.get_login_info()
    await bot.send_group_forward_msg(
        group_id=event.group_id,
        messages=[
            {
                "type": "node",
                "data": {
                    "name": login["nickname"],
                    "uin": event.self_id,
                    "content": content,
                },
            }
            for content in msg
        ],
    )

    await random_setu.finish()
