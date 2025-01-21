#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName :get_task_config.py
# @Time :2024/12/23 15:39
# @Author :Jiamid
from fastapi import APIRouter
from commonts.storage_manager import timer_task_storage
from commonts.base_model import BaseResponseModel
from pydantic import BaseModel, Field

router = APIRouter()


class TaskConfigModel(BaseModel):
    keywords: list[str] = Field(default=[])
    targets: list[str] = Field(default=[])
    search_num: int = Field(default=10)
    scroll_num: int = Field(default=7)
    ua: int = Field(default=4)
    webrtc: str = Field(default='proxy')
    ua_version: list[str] = Field(default=['131'])


class TaskConfigRespModel(BaseResponseModel):
    data: TaskConfigModel = Field(default=TaskConfigModel())


@router.get("/get_task_config", response_model=TaskConfigRespModel)
async def get_task_config():
    keywords = timer_task_storage.get_value("click_keywords", [])
    targets = timer_task_storage.get_value("targets", [])

    search_num = timer_task_storage.get_value("search_num", 10)
    scroll_num = timer_task_storage.get_value("scroll_num", 7)
    ua = timer_task_storage.get_value("ua", 4)
    webrtc = timer_task_storage.get_value("webrtc", "proxy")
    ua_version = timer_task_storage.get_value("ua_version", ["130"])
    return TaskConfigRespModel(data=TaskConfigModel(
        keywords=keywords,
        targets=targets,
        search_num=search_num,
        scroll_num=scroll_num,
        ua=ua,
        webrtc=webrtc,
        ua_version=ua_version
    ))
