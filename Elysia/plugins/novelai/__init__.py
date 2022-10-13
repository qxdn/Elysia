from .data_source import novelai
from .config import novelai_header, cloudserverapi_header
from Elysia.utils import requests
import httpx

from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message,
    Bot,
    MessageSegment,
    GroupMessageEvent,
)
import time

txt2image_matcher = novelai().on_command("生成色图", "使用文字生成色图", priority=2)

# @txt2image_matcher.handle()
async def novelai_txt2image(bot: Bot, event: MessageEvent):
    raw_seed = None
    raw_message = (
        event.get_message().extract_plain_text().replace("，", ",").replace("生成色图", "")
    )

    # TODO: 添加参数提取
    inputs = raw_message
    if not inputs:
        await txt2image_matcher.finish("请输入你想要生成的tag")
    seed = raw_seed or int(time.time())

    prehandle = Message()
    prehandle.append(MessageSegment.text("正在生成..."))

    # 发送预通知
    await bot.send(event, prehandle, at_sender=True)

    body = novelai.novelai_txt2body(seed, inputs)

    resp = await requests.post(
        "https://api.nya.la/ai/generate-image", json=body, headers=novelai_header
    )

    if resp.status_code != 201:
        data = resp.json()
        await txt2image_matcher.finish(f"生成失败，错误原因{data['error']}")

    img = resp.text
    img_byte = img.split("data:", 1)[1]
    result = Message()
    result.append(MessageSegment.image(f"base64://{img_byte}"))
    result.append(MessageSegment.text(f"seed={seed}"))
    await bot.send(event, result, at_sender=True)


@txt2image_matcher.handle()
async def cloudserverapi_txt2image(bot: Bot, event: MessageEvent):
    raw_seed = None
    raw_message = (
        event.get_message().extract_plain_text().replace("，", ",").replace("生成色图", "")
    )

    # TODO: 添加参数提取
    inputs = raw_message
    if not inputs:
        await txt2image_matcher.finish("请输入你想要生成的tag")
    seed = raw_seed or int(time.time())

    prehandle = Message()
    prehandle.append(MessageSegment.text("正在生成..."))

    # 发送预通知
    await bot.send(event, prehandle, at_sender=True)

    body = novelai.cloudserverapi_txt2body(seed, inputs)

    async with httpx.AsyncClient() as client:
        logger.debug(f"POST cloudserverapi  with \n: {body}")
        resp = await client.post(
            "https://cloudserverapi.com/generate-stream",
            headers=cloudserverapi_header,
            json=body,
            timeout=114514,
        )

    if resp.status_code != 200:
        await txt2image_matcher.finish(f"生成失败，错误原因{resp.status_code}")

    img = resp.text
    img_byte = img.split("data:", 1)[1]
    result = Message()
    result.append(MessageSegment.image(f"base64://{img_byte}"))
    result.append(MessageSegment.text(f"seed={seed}"))
    await bot.send(event, result, at_sender=True)
