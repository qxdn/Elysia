import time
from pydantic import BaseModel
from traceback import format_exc
from nonebot.adapters import Bot, Event
from nonebot.message import run_preprocessor


class ExceptionInfo(BaseModel):
    msg: str
    time: str
    content: str


class BaseBotException(Exception):
    def __init__(self, msg: str ):
        self.msg: str = msg
        self.time: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.content: str = format_exc()
        data = ExceptionInfo(msg=self.msg, time=self.time, content=self.content)
        super().__init__(data)


class WriteFileError(BaseBotException):
    def __init__(self, msg: str ) -> None:
        super().__init__(msg)


class ReadFileError(BaseBotException):
    def __init__(self, msg: str ):
        super().__init__(msg)

class RequestError(BaseBotException):
    def __init__(self, msg: str):
        super().__init__(msg)


@run_preprocessor
async def global_exception_handler(bot: Bot, event: Event):
    pass  # TODO: 实现全局异常处理
