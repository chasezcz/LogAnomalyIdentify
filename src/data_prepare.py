'''
@File    :   data_prepare.py
@Time    :   2021/11/19 13:48:19
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import argparse
import collections
import logging as log
import os
import random
from datetime import datetime
from os import path
from typing import List

import pandas as pd

from multideep.model import train
from sql.db import DB as db
from sql.db import ORIGIN_TABLE_LABELS
from utils.file_utils import (getContent, jsonLoad, mkdirIfNotExist, writeDict,
                              writeList)
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

    lines = []
    dic = set()
    for id in range(len(df)):
        data = df.iloc[id, ]
        if (len(data['eventId']) <= 5):
            continue
        seq = ' '.join([str(i) for i in data['eventId']])
        if seq not in dic:
            dic.add(seq)

            lines.append('{} {} {}'.format(
                data['date'],
                data['userId'],
                seq
            ))

    mkdirIfNotExist(basePath)
    all = trainSize + validationSize + testSize
    length = len(lines)
    flag1 = int(length * trainSize / all)
    flag2 = int(length * (trainSize+validationSize) / all)
    log.info("去重后，共得到序列 {} 条, 训练集 {} 条，验证集 {} 条，测试集 {} 条".format(
        length, flag1, flag2-flag1, length-flag2))
    if flag1 > 0:
        writeList(basePath + '/train', lines[:flag1])
    if flag1 < flag2:
        writeList(basePath + '/validation', lines[flag1:flag2])
    writeList(basePath + '/test', lines[flag2:])

    del lines
    del dic


def getEventMap(localPath: str, fromDB: bool = False):
    """
    getEventMap 获取EventMap

    Args:
        localPath (str): [description]
        fromDB (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    eventMap = dict()

    if fromDB:
        data = db.queryUrlEntrys()
        eventMap = dict()
        for line in data:
            eventMap[line[1]+':'+line[2]] = line[0]
    else:
        eventMap = jsonLoad(localPath)
    return eventMap


def generateDataset(userNum: int, threshold: int, eventMapPath: str = '', dataSample: bool = False, asTrain: bool = True):
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
    updateEventMap = False
    if len(eventMapPath) == 0:
        # 未指定
        eventMap = {'demo': 0}
        updateEventMap = True
    else:
        eventMap = getEventMap(eventMapPath)
        updateEventMap = False
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
    longSeq = pd.DataFrame()

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
        if updateEventMap:
            for event in tdf['event']:
                if event not in eventMap:
                    eventMap[event] = len(eventMap)

        tdf['eventId'] = tdf['event'].apply(
            lambda e: eventMap[e] if e in eventMap else 0)

        rdf = tdf.set_index('date').resample(ths).apply(
            lambda array: list(array)).reset_index()
        rdf = rdf.dropna(axis=0, subset=['eventId'])
        rdf['userId'] = user
        df = pd.concat([df, rdf], ignore_index=True)
        # 制作长序列
        lseq = []
        for seq in rdf['eventId']:
            cnter = collections.Counter(seq)
            lseq.extend([str(i) for i, _ in cnter.most_common(1)])
        lseqdf = pd.DataFrame({
            'eventId': [lseq]
        })
        lseqdf['userId'] = user
        lseqdf['date'] = tdf.iloc[0, ]['date']
        if len(lseq) > 0:
            longSeq = pd.concat([longSeq, lseqdf], ignore_index=True)
            #     longSeq.append('{} {} {}'.format(
            #         tdf.iloc[0, ]['date'], user, ' '.join(lseq)))
    if updateEventMap:
        writeDict(basePath + '/eventMap.json', eventMap)

    if dataSample:
        df = df.sample(frac=1).reset_index(drop=True)

    lseqPath = basePath+'/lseq'
    mkdirIfNotExist(lseqPath)

    if asTrain:
        trainDataFileGenerator(basePath, df,
                               trainSize=6,
                               validationSize=1,
                               testSize=3)
        trainDataFileGenerator(lseqPath, longSeq,
                               trainSize=6,
                               validationSize=3,
                               testSize=0)
    else:
        trainDataFileGenerator(basePath, df,
                               trainSize=0,
                               validationSize=0,
                               testSize=1)
        trainDataFileGenerator(lseqPath, longSeq,
                               trainSize=0,
                               validationSize=0,
                               testSize=1)
        # writeList(lseqPath+'/train', longSeq)
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
    parser.add_argument('--asTrain', type=bool, default=False, metavar='N',
                        help="如果此项为True，则为生成训练模型用的序列数据集，否则为对本地日志格式的读取")
    parser.add_argument('--eventMap', type=str, default='', metavar='N',
                        help='本地eventMap的路径')
    # log.debug(parser.parse_args().asTrain)

    generateDataset(parser.parse_args().userNum,
                    parser.parse_args().threshold, parser.parse_args().eventMap,
                    dataSample=False, asTrain=parser.parse_args().asTrain)
