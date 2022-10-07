import json
import re
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Set, Tuple, Type, Union

from nonebot.dependencies import Dependent
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.rule import Rule, command, keyword, regex
from nonebot.typing import T_Handler, T_PermissionChecker, T_RuleChecker, T_State
from pydantic import BaseModel

from .exceptions import ReadFileError, WriteFileError

# 持久化路径
SERVICES_DIR = Path(".") / "data" / "services"
# 创建路径
SERVICES_DIR.mkdir(parents=True, exist_ok=True)


class CommandInfo(BaseModel):
    type: str
    docs: str
    aliases: Union[list, set]


class ServiceInfo(BaseModel):
    service: str
    docs: str
    cmd_list: Dict[str, CommandInfo]
    enabled: bool  # 是否启用
    only_admin: bool  # 是否管理员
    disable_user: list  # 禁用用户
    disable_group: list  # 警用群组


class Service:
    """
    服务配置 参考[ATRI](https://github.com/Kyomotoi/ATRI)的设计
    {
        "service": "Service name",
        "docs": "Main helps and commands",
        "cmd_list": {
            "/cmd0": {
                "type": "Command type",
                "docs": "Command help",
                "aliases": ["More trigger ways."]
            }
        },
        disable_user: []
    }
    """

    def __init__(
        self,
        service: str,
        docs: str,
        only_admin: bool = False,
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        permission: Optional[Permission] = None,
        handlers: Optional[List[T_Handler]] = None,
        temp: bool = False,
        priority: int = 5,
        state: Optional[T_State] = None,
        main_cmd: str = str(),
    ):
        self.service = service  # NOSONAR
        self.docs = docs
        self.only_admin = only_admin
        self.rule = rule
        self.permission = permission
        self.handlers = handlers
        self.temp = temp
        self.priority = priority
        self.state = state
        self.main_cmd = (main_cmd,)

    def save_service(self, service_data: dict, service: str) -> None:
        """
        持久化服务
        """
        if not service:
            service = self.service

        path = SERVICES_DIR / f"{service}.json"
        if not path.is_file():
            self._generate_service_config(service, self.docs)

        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(service_data, indent=4, ensure_ascii=False))

    def load_service(self, service: str) -> dict:
        path = SERVICES_DIR / f"{service}.json"
        if not path.is_file():
            self._generate_service_config(service, self.docs)

        try:
            data = json.loads(path.read_bytes())
        except Exception:
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))
            self._generate_service_config(service, self.docs)
            data = json.loads(path.read_bytes())
        return data

    def _generate_service_config(self, service: str, docs: str = str()) -> None:
        """
        默认配置
        """
        path = SERVICES_DIR / f"{service}.json"
        data = ServiceInfo(
            service=service,
            docs=docs,
            cmd_list=dict(),
            enabled=True,
            only_admin=self.only_admin,
            disable_user=list(),
            disable_group=list(),
        )
        try:
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps(data.dict(), indent=4, ensure_ascii=False))
        except Exception:
            raise WriteFileError("Write service info failed!")

    def _save_cmds(self, cmds: dict) -> None:
        data = self.load_service(self.service)
        temp_data: dict = data["cmd_list"]
        temp_data.update(cmds)
        self.save_service(data, self.service)

    def _load_cmds(self) -> dict:
        path = SERVICES_DIR / f"{self.service}.json"
        if not path.is_file():
            self._generate_service_config(self.service, self.docs)

        data = json.loads(path.read_bytes())
        return data["cmd_list"]

    def on_message(
        self,
        name: str = str(),
        docs: str = str(),
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        permission: Optional[Union[Permission, T_PermissionChecker]] = None,
        handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
        block: bool = True,
        priority: int = 5,
        state: Optional[T_State] = None,
        **kwargs,
    ) -> Type[Matcher]:
        """
        on_message matcher
        """
        if not rule:
            rule = self.rule
        if not permission:
            permission = self.permission
        if not handlers:
            handlers = self.handlers
        if not state:
            state = self.state

        if name:
            cmd_list = self._load_cmds()

            name = name + "-onmsg"

            cmd_list[name] = CommandInfo(
                type="message", docs=docs, aliases=list()
            ).dict()
            self._save_cmds(cmd_list)

        matcher = Matcher.new(
            "message",
            Rule() & rule,
            Permission() | permission,
            module=ModuleType(self.service),
            temp=self.temp,
            priority=priority,
            block=block,
            handlers=handlers,
            default_state=state,
            **kwargs,
        )
        return matcher

    def on_command(
        self,
        cmd: Union[str, Tuple[str, ...]],
        docs: str,
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
        **kwargs,
    ) -> Type[Matcher]:
        """
        on_command matcher
        """
        cmd_list = self._load_cmds()
        if not rule:
            rule = self.rule
        if not aliases:
            aliases = set()

        if isinstance(cmd, tuple):
            cmd = ".".join(map(str, cmd))

        cmd_list[cmd] = CommandInfo(
            type="command", docs=docs, aliases=list(aliases)
        ).dict()
        self._save_cmds(cmd_list)
        commands = set([cmd]) | (aliases or set())
        return self.on_message(rule=command(*commands) & rule, block=True, **kwargs)

    def on_keyword(
        self,
        keywords: Set[str],
        docs: str,
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        **kwargs,
    ) -> Type[Matcher]:
        if not rule:
            rule = self.rule

        name = list(keywords)[0] + "-onkw"

        cmd_list = self._load_cmds()

        cmd_list[name] = CommandInfo(type="keyword", docs=docs, aliases=keywords).dict()
        self._save_cmds(cmd_list)

        return self.on_message(rule=keyword(*keywords) & rule, **kwargs)

    def on_regex(
        self,
        pattern: str,
        docs: str,
        flags: Union[int, re.RegexFlag] = 0,
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        **kwargs,
    ) -> Type[Matcher]:
        if not rule:
            rule = self.rule

        cmd_list = self._load_cmds()
        cmd_list[pattern] = CommandInfo(type="regex", docs=docs, aliases=list()).dict()
        self._save_cmds(cmd_list)

        return self.on_message(rule=regex(pattern, flags) & rule, **kwargs)


class ServiceTools(object):
    @staticmethod
    def save_service(service_data: dict, service: str):
        path = SERVICES_DIR / f"{service}.json"
        if not path.is_file():
            raise ReadFileError(
                f"Can't find service file: {service}\n"
                "Please delete all file in data/service/services\n"
                "And reboot bot."
            )

        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(service_data, indent=4, ensure_ascii=False))

    @staticmethod
    def load_service(service: str) -> dict:
        path = SERVICES_DIR / f"{service}.json"
        if not path.is_file():
            raise ReadFileError(
                f"Can't find service file: {service}\n"
                "Please delete all file in data/service/services\n"
                "And reboot bot."
            )

        with open(path, "r", encoding="utf-8") as r:
            data = json.loads(r.read())
        return data

    @classmethod
    def auth_service(cls, service, user_id: str = str(), group_id: str = str()) -> bool:
        """
        用户鉴权
        """
        data = cls.load_service(service)

        auth_global = data.get("enabled", True)
        auth_user = data.get("disable_user", list())
        auth_group = data.get("disable_group", list())

        if user_id:
            if user_id in auth_user:  # NOSONAR
                return False

        if group_id:
            if group_id in auth_group:
                return False
            else:
                return True

        if not auth_global:
            return False
        else:
            return True

    @classmethod
    def service_controller(cls, service: str, is_enabled: bool):
        data = cls.load_service(service)
        data["enabled"] = is_enabled
        cls.save_service(data, service)
