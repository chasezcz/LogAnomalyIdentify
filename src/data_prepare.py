'''
@File    :   data_prepare.py
@Time    :   2021/11/19 13:48:19
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import logging as log
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd


from sql.db import DB as db
from sql.db import ORIGIN_TABLE_LABELS
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
    df = pd.DataFrame(originLogs, columns=columns)
    log.debug(df)
    return df


if __name__ == '__main__':
    logInit(__file__, log.DEBUG)
    df = pd.read_pickle('data/173211-9739.pkl')
    df = pd.DataFrame(df)
    print(df.at(1, 'headers'))
