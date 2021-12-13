'''
@File    :   data_prepare.py
@Time    :   2021/11/19 13:48:19
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import argparse
import logging as log
import os
import random
from datetime import datetime
from os import path
from typing import List

import pandas as pd

from sql.db import DB as db
from sql.db import ORIGIN_TABLE_LABELS
from utils.file_utils import getContent, mkdirIfNotExist, writeDict, writeList
from utils.logger_utils import logInit


def getLogsFromDBByDate(columns: List[str] = [], startDate: str = "1996-01-01", endDate: str = "2022-12-12") -> pd.DataFrame:
    """
    getLogsFromDBByDate 获取某一时间段的日志，可支持获取日志的某几个字段

    Args:
        columns (List[str]): 想要获取的字段，如果此项为空，则默认获取全部字段
        startDate (str): 开始的日期
        endDate (str): 结束的日期

    Returns:
        pd.DataFrame: 返回的日志数据
    """
    if (columns == None or len(columns) == 0):
        columns = ORIGIN_TABLE_LABELS
    startf = datetime.fromisoformat(startDate).timestamp()
    endf = datetime.fromisoformat(endDate).timestamp()
    rangeLabel = 'time'
    start, end = '%.3f' % startf, '%.3f' % endf
    log.debug("获取日志字段 %s, 要求%s 在 [%s %s] 范围内" % (
        ','.join(columns), rangeLabel, start, end))

    originLogs = db.queryOriginWithRange(columns, rangeLabel, start, end)
    df = pd.DataFrame(originLogs, columns=columns)
    # log.debug(df)
    return df


def getLogsFromDBByUserID(userID: str, columns: List[str] = []) -> pd.DataFrame:
    """
    getLogsFromDBByDate 获取某一时间段的日志，可支持获取日志的某几个字段

    Args:
        userID (str): userID
        columns (List[str]): 想要获取的字段，如果此项为空，则默认获取全部字段
    Returns:
        pd.DataFrame: 返回的日志数据

    ```
    userID = '173211-9739'
    df = getLogsFromDBByUserID(
        userID, ['time', 'urlEntry', 'method', 'parameterName', 'headers', 'name', 'ip'])
    ```
    df.to_pickle('data/%s.pkl' % userID)
    """
    if (columns == None or len(columns) == 0):
        columns = ORIGIN_TABLE_LABELS

    equalLabel = 'userID'

    log.debug("获取日志字段 %s, 要求 userID 为 %s " % (','.join(columns),  userID))

    originLogs = db.queryOriginWithEqual(columns, equalLabel, userID)
    log.debug("获取到数据%d条，columns为%s" % (len(originLogs), ','.join(columns)))
    df = pd.DataFrame(originLogs, columns=columns)
    # log.debug(df)
    return df


def deeplogDfTransfer(df, event_id_map):
    df = df[['date', 'event']]
    df['EventId'] = df['event'].apply(
        lambda e: event_id_map[e] if event_id_map.get(e) else 0)
    deeplog_df = df.set_index('date').resample(
        '5min').apply(lambda array: list(array)).reset_index()
    return deeplog_df


def trainDataFileGenerator(basePath: str, df: pd.DataFrame, trainSize=5, validationSize=2, testSize=3):
    """
    trainDataFileGenerator 生成序列数据文件

    Args:
        basePath (str): 文件存档的基础路径
        df (pd.DataFrame): 数据
        trainSize (int, optional): 训练集所占比. Defaults to 5.
        validationSize (int, optional): 验证集所占比. Defaults to 2.
        testSize (int, optional): 测试集所占比. Defaults to 3.
    """

    lines = set()
    for event_id_list in df['EventId']:
        if (len(event_id_list) <= 5):
            continue
        lines.add(' '.join([str(id) for id in event_id_list]))
    lines = list(lines)
    mkdirIfNotExist(basePath)
    all = trainSize + validationSize + testSize
    length = len(lines)
    flag1 = int(length * trainSize / all)
    flag2 = int(length * (trainSize+validationSize) / all)
    log.info("去重后，共得到序列 {} 条, 训练集 {} 条，验证集 {} 条，测试集 {} 条".format(
        length, flag1, flag2-flag1, length-flag2))

    writeList(basePath + '/train', lines[:flag1])
    writeList(basePath + '/validation', lines[flag1:flag2])
    writeList(basePath + '/test', lines[flag2:])
    del lines


def getEventMap():
    """
    getEventMap 获取所有的Event, method:urlEntry
    """
    data = db.queryUrlEntrys()
    eventMap = dict()
    for line in data:
        eventMap[line[1]+':'+line[2]] = line[0]
    return eventMap


def generateDataset(userNum: int, threshold: int):
    """
    generateDataset 生成数据集，包括 训练集，验证集以及测试集

    Args:
        userNum (int): 用户数据集的用户数量
        threshold (int): 时间窗口的阈值
    """
    usersListPath = 'data/users.txt'
    columns = [
        'time', 'urlEntry', 'method'
    ]

    eventMap = {'demo': 0}
    users = getContent(usersListPath)
    ths = "%dmin" % threshold

    userNum = len(users) if userNum > len(users) else userNum
    users = random.sample(users, userNum)
    # train : Validation : test = 5 : 2 : 3
    basePath = 'data/%d_%d' % (userNum, threshold)
    if not path.exists(basePath):
        # create
        os.makedirs(basePath)
    df = pd.DataFrame()

    for id, user in enumerate(users):
        log.debug("开始处理用户%s, %d/%d" % (user, id, userNum))
        tdf = getLogsFromDBByUserID(user, columns)
        log.debug("共获取到%d条数据" % len(tdf))

        tdf['date'] = tdf['time'].apply(
            lambda timestamp: datetime.fromtimestamp(timestamp))
        tdf['event'] = tdf['method'] + ':' + tdf['urlEntry']
        tdf = tdf[['date', 'event']]
        # update event map
        # eventMap = {event: id for id, event in enumerate(
        #     df['event'].value_counts().keys())}
        for event in tdf['event']:
            if event not in eventMap:
                eventMap[event] = len(eventMap)

        tdf['EventId'] = tdf['event'].apply(lambda e: eventMap[e])
        deeplogDf = tdf.set_index('date').resample(ths).apply(
            lambda array: list(array)).reset_index()
        df = pd.concat([df, deeplogDf], ignore_index=True)

    writeDict(basePath + '/eventMap.json', eventMap)

    df = df.sample(frac=1).reset_index(drop=True)
    # print(df)
    trainDataFileGenerator(basePath, df)
    log.info("%s 保存完毕" % user)


if __name__ == '__main__':
    logInit(__file__, log.DEBUG, isStreaming=True)
    # df = pd.read_pickle('data/173211-9739.pkl')
    # df = pd.DataFrame(df)

    # print(df.at(1, 'headers'))
    # res = getEventMap()
    # print(res)
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument('--userNum', type=int, default=10, metavar='N',
                        help='用于制作数据集的用户数量 (default: 10)')
    parser.add_argument('--threshold', type=int, default=30, metavar='N',
                        help='时间窗口阈值，一个时间窗口内的日志会判断为同一个session (default: 30)')

    generateDataset(parser.parse_args().userNum, parser.parse_args().threshold)
