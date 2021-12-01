'''
@File    :   data_prepare.py
@Time    :   2021/11/19 13:48:19
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import logging as log
import random
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd

from sql.db import DB as db
from sql.db import ORIGIN_TABLE_LABELS
from utils.file_utils import getContent, writeDict
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
    log.debug(df)
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
    log.debug(df)
    return df


def deeplogDfTransfer(df, event_id_map):
    df = df[['date', 'event']]
    df['EventId'] = df['event'].apply(
        lambda e: event_id_map[e] if event_id_map.get(e) else -1)
    deeplog_df = df.set_index('date').resample(
        '5min').apply(lambda array: list(array)).reset_index()
    return deeplog_df


def trainDataFileGenerator(filename: str, df: pd.DataFrame):
    """
    trainDataFileGenerator 生成训练数据文件

    Args:
        filename (str): 训练数据的对应文件名
        df (pd.DataFrame): 数据
    """
    with open(filename, 'a') as f:
        for event_id_list in df['EventId']:
            if (len(event_id_list) == 0):
                continue
            for event_id in event_id_list:
                f.write(str(event_id) + ' ')
            f.write('\n')


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
    usersListPath = 'data/users.txt'
    columns = [
        'time', 'urlEntry', 'method'
    ]
    ths = "%dmin" % threshold
    trainFilePath = 'data/train_%d_%d' % (userNum, threshold)

    eventMap = dict()
    users = getContent(usersListPath)
    if userNum > len(users):
        userNum = len(users)
    targetUsers = random.sample(users, userNum)

    for id, user in enumerate(targetUsers):
        user = user.strip()
        log.debug("开始处理用户%s, %d/%d" % (user, id, len(targetUsers)))
        df = getLogsFromDBByUserID(user, columns)
        log.debug("共获取到%d条数据" % len(df))

        df['date'] = df['time'].apply(
            lambda timestamp: datetime.fromtimestamp(timestamp))
        df['event'] = df['method'] + ':' + df['urlEntry']
        df = df[['date', 'event']]

        # update event map
        for event in df['event']:
            if event in eventMap:
                continue
            eventMap[event] = len(eventMap)

        df['EventId'] = df['event'].apply(
            lambda e: eventMap[e] if eventMap.get(e) else -1)
        deeplogDf = df.set_index('date').resample(
            ths).apply(lambda array: list(array)).reset_index()
        trainDataFileGenerator(trainFilePath, deeplogDf)
        log.info("%s 保存完毕" % user)
    writeDict('data/eventMap.json', eventMap)


if __name__ == '__main__':
    logInit(__file__, log.DEBUG)
    # df = pd.read_pickle('data/173211-9739.pkl')
    # df = pd.DataFrame(df)

    # print(df.at(1, 'headers'))
    # res = getEventMap()
    # print(res)
    generateDataset(30, 30)
