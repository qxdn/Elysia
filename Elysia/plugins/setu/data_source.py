from Elysia.utils import requests
from Elysia.service import Service
from Elysia.rule import is_in_service,to_bot
from .config import Setu_Type

LOLICON_URL = "https://api.lolicon.app/setu/v2"

class Setu(Service):
    '''
    色图插件
    '''
    def __init__(self) -> None:
        Service.__init__(
            self,"随机色图","使用lolicon api搜索随机色图",rule=is_in_service("随机色图")&to_bot
        )
    
    @classmethod
    async def random_setu(cls,r18=Setu_Type.NON_R18,tag:list=None):
        '''
        无tag随机色图
        '''
        params = {
            "r18": r18,
            "tag": tag
        }
        result = await requests.post(LOLICON_URL,json=params)
        data:dict = result.json()
        data: list = data.get("data",None)
        if not data:
            return "",None
        
        data:dict = data[0]
        title = data.get("title", "未知")
        p_id = data.get("pid", "未知")
        url: str = data["urls"].get("original", "ignore")
        info = f"title:{title},pid:{p_id}"
        return info,url
        
        
