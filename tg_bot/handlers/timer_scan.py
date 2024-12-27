# -*- coding: utf-8 -*-
# @Time    : 2024/7/30 14:28
# @Author  : JIAMID
# @Email   : jiamid@qq.com
# @File    : timer_scan.py
# @Software: PyCharm
import itertools
from loguru import logger
from datetime import datetime
from commonts.storage_manager import timer_task_storage
from commonts.storage_manager import proxy_manager
from commonts.storage_manager import history_html_storage
from commonts.json_manager import json_manager
from commonts.util import to_escape_string
from commonts.search import Google
from commonts.async_task_manager import AsyncTaskManager
from tg_bot.bot import send_message_to_bot
from commonts.settings import settings

os_map = {
    0: None,
    1: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    2: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    3: 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    4: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
}
os_name_map = {
    1: 'WIN',
    2: 'IOS',
    3: 'ANDROID',
    4: 'MAC',
}


async def scan_one(keyword: str, os: int, region: str, chat_ids: list,
                   result_list: list) -> None:
    logger.info(f'start run scan {keyword} {os} {region}')
    try:
        google_client = Google(proxy_manager.get_proxy_by_region(region))
        result, msg = await google_client.go(keyword, 3, os_map.get(os, None))
        if result:
            result_msg = (f'*{to_escape_string(keyword)}* \nregion:{region} os:{os_name_map.get(os, os)}\n'
                          f'_搜索结果_ \n')
            index = 0
            for k, v in result.items():
                domain = v.get('domain')
                rw = v.get('rw')
                if not domain:
                    logger.info(f'no domain {v}')
                    result_msg += f'>domain: [{index}]({to_escape_string(rw)})\n'
                    domain = rw
                else:
                    result_msg += f'>domain:{to_escape_string(v["domain"])}\n'
                index += 1
                # result_msg += f'[{index}号]({to_escape_string(k)})\n'
                # result_msg += f'>domain:{to_escape_string(v["domain"])}\n'
                result_list.append({
                    'keyword': keyword,
                    'os': os_name_map.get(os, os),
                    'region': region,
                    'domain': domain,
                    'create_at': datetime.now().strftime('%m-%d %H:%M:%S')
                })
            logger.info(f'found ad {index} from {keyword} {os} {region}')
            for chat_id in chat_ids:
                await send_message_to_bot(chat_id, result_msg, parse_mode='MarkdownV2')
        else:
            logger.info(f'not found ad {keyword} {os} {region}')
    except Exception as e:
        logger.error(f'run {keyword} {os} {region} fail {e}')


def decimal_to_base36(n):
    if n == 0:
        return '0'
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''

    while n > 0:
        n, remainder = divmod(n, 36)
        result = digits[remainder] + result

    return result


async def do_scan() -> None:
    """Send the alarm message."""
    keyword_list = timer_task_storage.get_value('keywords', [])
    sem = timer_task_storage.get_value('sem', 5)
    logger.info(f'start run scan {keyword_list}')
    chat_ids = timer_task_storage.get_value('chat_ids', [])
    if (not keyword_list) or (not chat_ids):
        logger.info(f'scan task not keyword or chat_ids')
        return
    os_list = [2, 4]
    region_list = list(proxy_manager.proxy_map.keys())
    task_gen = itertools.product(keyword_list, os_list, region_list)
    result = []
    task_manager = AsyncTaskManager(sem)
    for keyword, os, region in task_gen:
        await task_manager.add_task(scan_one, keyword=keyword, os=os, region=region,
                                    chat_ids=chat_ids, result_list=result)
    await task_manager.run()
    if result:
        now = datetime.now()
        now_ts = int(now.timestamp())
        ts_id = decimal_to_base36(now_ts)
        filename = f'r{ts_id}'
        json_manager.save_file(result, filename)
        history_list: list = history_html_storage.get_value('history', [])
        history_list.append({now.strftime('%Y-%m-%d %H:%M:%S'): filename})
        history_list = history_list[-50:]
        history_html_storage.set_value('history', history_list)
        text = f'访问以下网站查看结果\n{settings.base_webhook_url}/r/{filename}'
        for chat_id in chat_ids:
            await send_message_to_bot(chat_id, text)
    logger.info('success to end scan task')
