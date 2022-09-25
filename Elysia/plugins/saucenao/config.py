
from pydantic import BaseModel,Extra


class Config(BaseModel,extra=Extra.ignore):
    saucenao_api: str
