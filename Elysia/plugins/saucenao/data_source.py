from random import choice
from typing import Optional, Tuple

from Elysia.exceptions import RequestError
from Elysia.rule import is_in_service
from Elysia.service import Service
from Elysia.utils import requests

from .db import SauceNAO_Index


class SearchResult():
    
    @property
    def title(self)->str:
        return self._title
    @title.setter
    def title(self,_title:str):
        self._title = _title
    @property
    def similarity(self)->str:
        return self._similarity
    @similarity.setter
    def similarity(self,_similarity:str):
        self._similarity = _similarity
    @property
    def image_url(self)->str:
        return self._image_url
    @image_url.setter
    def image_url(self,_image_url:str):
        self._image_url = _image_url
    @property
    def thumbnail(self)->str:
        return self._thumbnail
    @thumbnail.setter
    def thumbnail(self,_thumbnail:str):
        self._thumbnail = _thumbnail

    def __str__(self) -> str:
        return (
            f"相似度:{self._similarity}\n"
            f"标题:{self._title}\n"
            f"链接{self._image_url}\n"
        )


# saucenao url
BASE_URL = "https://saucenao.com/search.php"


class SauceNAO(Service):
    def __init__(
        self,
        api_key: str,
        testmode=0,  # 为1时每个索引只有一个输出
        dbmask: Optional[int] = None,
        dbmaski: Optional[int] = None,
        db: int = SauceNAO_Index.ALL,
        numres: int = 3,  # 结果数
        output_type: int = 2,  # json
        hide: int = 0,  # 隐藏控制
        threshold: float = 70,
        **kwargs
    ) -> None:
        Service.__init__(self,"以图搜图", "搜索图片出处，基于SauceNAO", rule=is_in_service("以图搜图"))

        params = {
            "api_key": api_key,
            "test_mode": testmode,
            "db": db,
            "numres": numres,
            "output_type": output_type,
            "hide": hide,
        }

        if dbmask != None:
            params["dbmask"] = dbmask
        if dbmaski != None:
            params["dbmaski"] = dbmaski

        # 配置
        self.params = params
        self.threshold = threshold

    async def search_from_file(self, files):
        """
        搜索文件
        """
        return await self._search(self.params, {"file": files})

    async def search_from_url(self, url: str):
        """
        搜索url
        """
        params = self.params.copy()
        params["url"] = url
        return await self._search(params)

    async def _request(self, params: dict, files=None) -> dict:
        try:
            response = await requests.post(BASE_URL, params=params, files=files)
        except Exception:
            raise RequestError("网络请求错误")
        # 返回json
        return response.json()

    def _generate_result(self, result: dict) -> SearchResult:
        r = SearchResult()
        r.title = result["data"].get("title", result["header"]["index_name"])
        r.similarity = result["header"]["similarity"]
        r.image_url = choice(result["data"].get("ext_urls", ["None"]))
        r.thumbnail = result["header"]["thumbnail"]
        return r

    async def _search(self, params: dict, files=None) -> Tuple[list, bool]:
        data = await self._request(params, files)
        result = data.get("results", None)
        if None == result:
            return list(),False

        size = len(result)

        r = list()
        find = False
        for i in range(size):
            _r = self._generate_result(result[i])
            if float(_r.similarity) >= self.threshold:
                find = True
            r.append(_r)

        return r, find
