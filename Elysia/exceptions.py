import time
from typing import Optional
from pydantic import BaseModel
from traceback import format_exc
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
from nonebot.log import logger

class ExceptionInfo(BaseModel):
    msg: str
    time: str
    content: str


class BaseBotException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg
        self.time: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.content: str = format_exc()
        data = ExceptionInfo(msg=self.msg, time=self.time, content=self.content)
        super().__init__(data)


class WriteFileError(BaseBotException):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class ReadFileError(BaseBotException):
    def __init__(self, msg: str):
        super().__init__(msg)


class RequestError(BaseBotException):
    def __init__(self, msg: str):
        super().__init__(msg)


@run_postprocessor
async def global_exception_handler(
    bot: Bot, event: Event, matcher: Matcher, exception: Optional[Exception]
)->None:
    # TODO: 实现全局异常处理
    if not exception:
        # 无异常
        return 
    logger.error(exception)