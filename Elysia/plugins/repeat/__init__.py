
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.log import logger

from .data_source import Repeat

repeat = Repeat()

repeat_matcher = repeat.on_message("复读机","自动复读消息",priority=10)


@repeat_matcher.handle([Cooldown(2)])
async def repeat_message(bot:Bot,event:GroupMessageEvent):
    gid = event.group_id
    answer = repeat.repeatMessage(event)
    if answer != None:
        logger.info(f"[复读机]发送回复:{answer}")
        await bot.send_group_msg(group_id=gid,message=answer,auto_escape=False)
    repeat_matcher.finish()
