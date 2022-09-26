import re
from typing import Dict

from Elysia.rule import is_in_service
from Elysia.service import Service
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.log import logger


class Repeat(Service):
    def __init__(self, count: int = 3, **kwargs):
        Service.__init__(
            self, "复读机", "复读群友消息",rule=is_in_service("复读机"),permission=GROUP
        )
        self.count = count
        self.repeatDict: Dict[int : Dict[str:int]] = {}
    
    # 消息预处理
    def messagePreprocess(self,message: str):
        raw_message = message
        contained_images = {}
        images = re.findall(r'\[CQ:image.*?]', message)
        for i in images:
            contained_images.update({i: [re.findall(r'url=(.*?)[,\]]', i)[0][0], re.findall(r'file=(.*?)[,\]]', i)[0][0]]})
        for i in contained_images:
            message = message.replace(i, f'[{contained_images[i][1]}]')
        return message, raw_message

    def repeatMessage(self, event: GroupMessageEvent):
        group_id = event.group_id
        message,raw_message = self.messagePreprocess(str(event.message))
        counter = self.repeatDict.get(group_id, None)
        if None == counter:
            '''
            该群为空
            '''
            self.repeatDict[group_id] = {"count": 1, "message": message}  # 计数器
            return None
        elif counter["message"] != message:
            counter["count"] = 1
            counter["message"] = message
            return None
        else:
            counter["count"] += 1
            
        # counter到了
        logger.debug(f"群号{group_id}重复次数{counter}")
        if counter["count"] == self.count:
            del self.repeatDict[group_id]
            return raw_message
