from nonebot.adapters import Event
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from .service import ServiceTools

def is_in_service(service:str):
    '''
    服务鉴权
    service；服务名
    '''
    async def _is_in_service(event:Event) -> bool:
        result = ServiceTools().auth_service(service)
        if not result:
            # 全局插件是否启动
            return False

        if isinstance(event, PrivateMessageEvent):
            # 私聊消息
            user_id = event.get_user_id()
            result = ServiceTools().auth_service(service, user_id)
            return result
        elif isinstance(event, GroupMessageEvent):
            # 群发消息
            user_id = event.get_user_id()
            group_id = str(event.group_id)
            result = ServiceTools().auth_service(service, user_id, group_id)
            return result
        else:
            return True
    
    return Rule(_is_in_service)


def to_bot():
    async def _to_bot(event: Event) -> bool:
        return event.is_tome()
    
    return Rule(_to_bot)

def is_private_msg():
    async def _is_private_msg(event:Event)->bool:
        if isinstance(event,PrivateMessageEvent):
            return True
        return False
    return Rule(_is_private_msg)

def is_group_msg():
    async def _is_group_msg(event:Event)->bool:
        if isinstance(event,GroupMessageEvent):
            return True
        return False
    return Rule(_is_group_msg)