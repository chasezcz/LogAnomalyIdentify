'''
@File    :   main.py
@Time    :   2021/08/18 14:01:17
@Author  :   Chengze Zhang 
@Contact :   chengze1996@gmail.com
@License :   Copyright (c) 2020 Chengze Zhang
'''

# here put the import lib
import os

from tools.url_match import UrlMatcher, generateMapping


# config
MAPPING_PATH = r'data\mapping'


def preProcess():
    ''' 预处理，整合数据，转化url'''
    if not os.path.exists(MAPPING_PATH):
        generateMapping()

    match = UrlMatcher()
    

if __name__ == '__main__':

    preProcess()
