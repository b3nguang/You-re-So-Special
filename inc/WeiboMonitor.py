# -*- coding: utf-8 -*-

import requests
import sys
import logging
import os

from typing import List, Dict, Optional

# 设置日志记录的基本配置
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WeiboMonitor:
    def __init__(self):
        """
        初始化微博监控类。
        设置请求头信息以及关注的用户UID列表。
        
        属性：
        - reqHeaders (Dict[str, str]): 请求头信息
        - uid (List[str]): 关注用户的UID列表
        """
        self.reqHeaders: Dict[str, str] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Connection': 'close',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        uid = os.environ["WEIBO_UIDS"]  # 这里添加关注人的uid
        self.uid: List[str] = uid.split(',')  

    def get_weibo_info(self) -> None:
        """
        获取微博信息。
        遍历uid列表，获取每个用户微博的容器索引URL。
        """
        try:
            self.weibo_info: List[str] = []
            for uid in self.uid:
                user_info_url: str = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}'
                res = requests.get(user_info_url, headers=self.reqHeaders)
                for j in res.json()['data']['tabsInfo']['tabs']:
                    if j['tab_type'] == 'weibo':
                        container_url: str = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={j["containerid"]}'
                        self.weibo_info.append(container_url)
        except Exception as e:
            logging.debug(e)
            sys.exit()

    def get_wb_queue(self) -> None:
        """
        获取已发布微博的ID队列。
        收集每个用户微博容器索引中的微博ID，并保存到文件中。
        """
        try:
            self.item_ids: List[str] = []
            for info_url in self.weibo_info:
                res = requests.get(info_url, headers=self.reqHeaders)
                with open('weiboId.txt', 'a') as f:
                    for j in res.json()['data']['cards']:
                        if j['card_type'] == 9:
                            f.write(f"{j['mblog']['id']}\n")
                            self.item_ids.append(j['mblog']['id'])
            logging.info('微博数目获取成功')
            logging.info(f'目前有 {len(self.item_ids)} 条微博')
        except Exception as e:
            logging.debug(e)
            sys.exit()

    def start_monitor(self) -> Optional[Dict[str, str]]:
        """
        开始监控。
        检查是否有新的微博发布，如果有，则记录微博信息并返回。
        
        返回值：
        - return_dict (Dict[str, str]): 新发布的微博内容（如果存在的话）
        """
        return_dict: Dict[str, str] = {}  # 获取微博相关内容，编辑为钉钉消息
        try:
            item_ids: List[str] = []
            with open('weiboID.txt', 'r') as f:
                for line in f.readlines():
                    item_ids.append(line.strip('\n'))
            for message_url in self.weibo_info:
                res = requests.get(message_url, headers=self.reqHeaders)
                for j in res.json()['data']['cards']:
                    if j['card_type'] == 9:
                        if str(j['mblog']['id']) not in item_ids:
                            with open('weiboID.txt', 'a') as f:
                                f.write(f"{j['mblog']['id']}\n")
                            logging.info('发微博啦!!!')
                            logging.info(f'目前有 {len(item_ids) + 1} 条微博')
                            return_dict['created_at'] = j['mblog']['created_at']
                            return_dict['text'] = j['mblog']['text']
                            return_dict['source'] = j['mblog']['source']
                            return_dict['nick_name'] = j['mblog']['user']['screen_name']
                            return return_dict
        except Exception as e:
            logging.debug(e)
            sys.exit()