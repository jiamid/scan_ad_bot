#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName :base_list_storage_api.py
# @Time :2024/12/26 2:59
# @Author :Jiamid
from loguru import logger
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from commonts.storage_manager import StorageManager


class BaseListStorageApi:
    """
    用于快速生成对List模型增删查管理的BotAPI
    """

    def __init__(self, storage_manager: StorageManager, key: str, cmd_base_name: str):
        self.storage_manager = storage_manager
        self.key = key
        self.cmd_base_name = cmd_base_name

    def register(self, register_router: Router):
        """
        register api to router
        """
        register_router.message(Command(f"list_{self.cmd_base_name.lower()}s"))(self.api_list)
        register_router.message(Command(f"add_{self.cmd_base_name.lower()}"))(self.api_add)
        register_router.message(Command(f"del_{self.cmd_base_name.lower()}"))(self.api_del)

    def __call__(self, register_router: Router):
        """
        same as register
        """
        self.register(register_router)
        return self

    async def api_list(self, message: Message) -> None:
        """
        /add_[cmd_base_name]s
        """
        try:
            data = self.storage_manager.get_value(self.key, [])
            _str = '\n'.join(data)
            text = f"{self.cmd_base_name.title()}: \n{_str}"
            await message.answer(text)
        except Exception as e:
            logger.error(f'list {self.cmd_base_name} fail {e}')
            await message.answer(f'list {self.cmd_base_name} error')

    async def api_add(self, message: Message) -> None:
        """
        /add_[cmd_base_name] args
        """
        try:
            args = message.text.split()[1:]
            if args:
                data = args[0]
                text = f"add {self.cmd_base_name.title()}: {data} success"
                self.storage_manager.add_to_key(self.key, data)
            else:
                text = f"请携带要添加的内容"
            logger.info(text)
            await message.answer(text)
        except Exception as e:
            logger.error(f'add {self.cmd_base_name.title()} fail {e}')
            await message.answer(f'add {self.cmd_base_name.title()} error, check arg')

    async def api_del(self, message: Message) -> None:
        """
        /del_[cmd_base_name] args
        """
        try:
            args = message.text.split()[1:]
            if args:
                data = args[0]
                text = f"del {self.cmd_base_name.title()}: {data} success"
                self.storage_manager.del_from_key(self.key, data)
            else:
                text = f"请携带要删除的内容"
            logger.info(text)
            await message.answer(text)
        except Exception as e:
            logger.error(f'del {self.cmd_base_name.title()} fail {e}')
            await message.answer(f'del {self.cmd_base_name.title()} error, check arg')