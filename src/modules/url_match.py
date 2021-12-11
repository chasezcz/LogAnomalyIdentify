'''
@File    :   url_match.py
@Time    :   2021/11/18 21:03:27
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import re
from modules.url_entry import UrlEntry
from typing import List
import logging


class UrlMatcher(object):
    """
    UrlMatcher 拥有所有urlEntry的库表，可以支持对单条 dirtyUrl 的匹配与归一化
    """

    def __init__(self, entrys: List[UrlEntry]) -> None:
        """
        __init__ 初始化函数，从 entrys 生成自己的规则库

        Args:
            entrys (List[UrlEntry]): urlEntry 的全集
        """
        self.entrys = {}
        for entry in entrys:
            if entry.module not in self.entrys:
                self.entrys[entry.module] = {}
            if entry.method not in self.entrys[entry.module]:
                self.entrys[entry.module][entry.method] = {}
            if entry.length not in self.entrys[entry.module][entry.method]:
                self.entrys[entry.module][entry.method][entry.length] = []
            self.entrys[entry.module][entry.method][entry.length].append(entry)

    def convert(self, url: str, method: str) -> str:
        """
        convert 把url 转换为 rule 规则串

        Args:
            url (str): 原url
            method (str): http method

        Returns:
            str: 符合的 urlEntry
        """
        url = '/' + url.strip('/')
        length = len(url.split("/"))
        module = url.split('/')[1]
        try:
            for entry in self.entrys[module][method][length]:
                if entry.isMatch(url):
                    return entry.url
        except Exception as e:
            logging.debug(e)
            return url


if __name__ == '__main__':
    # matcher = UrlMatcher()
    # print(matcher.convert(
    #     "/ic/cover/lists", "PUT"))
    # generateMapping()
    pass
