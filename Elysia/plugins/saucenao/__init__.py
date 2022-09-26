import json
from random import choice
from typing import List

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.adapters.onebot.v11.helpers import Cooldown, extract_image_urls
from nonebot.log import logger
from nonebot.utils import DataclassEncoder

from .config import Config
from .data_source import SauceNAO, SearchResult

_search_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])

plugin_config: Config = Config.parse_obj(get_driver().config)


saucenao = SauceNAO(api_key=plugin_config.saucenao_api)

saucenao_matcher = saucenao.on_command("搜图", "通过图片反向查询出处")


async def _deal_search(event: MessageEvent):
    """
    处理搜索图片
    """
    img = extract_image_urls(event.message)
    if not img:
        logger.info("[以图搜图]输入的不是图片")
        await saucenao_matcher.finish("请发送图片而不是其他东西！！")

    return await saucenao.search_from_url(img[0])


def _generate_message(result: SearchResult) -> Message:
    """
    将结果转换为消息
    """
    return Message(
        [
            MessageSegment.text(f"标题:{result.title}\n"),
            MessageSegment.text(f"相似度:{result.similarity}%\n"),
            MessageSegment.image(result.thumbnail),
            MessageSegment.text(f"\n链接:{result.image_url}\n"),
        ]
    )


def _generate_group_forward_message(results: List[SearchResult]):
    """
    将结果转为转发消息防止风控
    """
    messages: Message = [_generate_message(result) for result in results]
    data_dict = json.loads(json.dumps(messages, cls=DataclassEncoder))
    return data_dict


@saucenao_matcher.handle([Cooldown(5, prompt=_search_flmt_notice)])
async def _deal_search_private(event: PrivateMessageEvent):
    results, _ = await _deal_search(event)

    message_list = Message()
    for result in results:
        message_list.extend(_generate_message(result))

    await saucenao_matcher.finish(message_list)


@saucenao_matcher.handle([Cooldown(5, prompt=_search_flmt_notice)])
async def _deal_search_group(bot: Bot, event: GroupMessageEvent):
    results, _ = await _deal_search(event)

    data_dict = _generate_group_forward_message(results)
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
            for content in data_dict
        ],
    )

    await saucenao_matcher.finish()
