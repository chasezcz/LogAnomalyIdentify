'''
@File    :   url_match.py
@Time    :   2021/08/17 11:01:10
@Author  :   Chengze Zhang 
@Contact :   chengze1996@gmail.com
@License :   Copyright (c) 2020 Chengze Zhang
'''

# here put the import lib

import os
import shutil
import re
import json
import pickle
from tools.files import getFilesByPath

# config
URLS_PATH = r'D:\Workspace\src\urlmatch\urls'
URLS_FORMAT = '.urls'
# static var
HTTPMETHODs = ["GET", "POST", "PUT", "DELETE", "OPTION"]


class UrlRule(object):
    module = ""  # 模块名
    method = ""  # http 方法
    url = ""    # 地址pattern
    length = 0  # url 的substr 数量

    def __init__(self) -> None:
        super().__init__()

    def __init__(self, origin: str) -> None:
        super().__init__()

        ss = origin.split()

        self.module = ss[0]
        self.method = ss[1]
        self.url = '/' + ss[2].strip('/')
        self.length = len(self.url.split("/"))
        pattern = re.sub(r'\{[^/]{1,100}\}',
                         r'[^/]{2,100}', self.url, count=100)

        self.pattern = re.compile(pattern)


class UrlMatcher(object):
    '''给url进行归一化'''
    rules = {}

    def __init__(self) -> None:
        super().__init__()
        for urlsFile in getFilesByPath(URLS_PATH, URLS_FORMAT):

            with open(urlsFile, 'r') as f:
                for line in f:
                    rule = UrlRule(line)
                    if rule.method not in self.rules:
                        self.rules[rule.method] = {}
                    if rule.length not in self.rules[rule.method]:
                        self.rules[rule.method][rule.length] = []
                    self.rules[rule.method][rule.length].append(rule)

    def convert(self, url: str, method: str) -> str:
        ''' 把url 转换为 rule 规则串'''
        url = '/' + url.strip('/')
        length = len(url.split("/"))
        if method in self.rules and length in self.rules[method]:
            for rule in self.rules[method][length]:
                if re.match(rule.pattern, url) != None:
                    return rule.url
        return url


def generateMapping(mapping_path: str = r"data\mapping"):
    '''生成映射表'''
    match = UrlMatcher()
    idx = 0
    url2idx = {}
    idx2url = {}
    for method in match.rules.keys():
        for length in match.rules[method]:
            for rule in match.rules[method][length]:
                key = "{:0>4d}".format(idx)
                url2idx[rule.url], idx2url[key] = key, rule.url
                idx += 1
    with open(mapping_path+'url2idx.json', 'w') as f:
        json.dump(url2idx, f)
    with open(mapping_path+'idx2url.json', 'w') as f:
        json.dump(idx2url, f)


if __name__ == '__main__':
    # matcher = UrlMatcher()
    # print(matcher.convert(
    #     "/ic/cover/lists", "PUT"))
    # generateMapping()
    pass
