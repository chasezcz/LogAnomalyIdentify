'''
@File    :   first_log_to_db.py
@Time    :   2021/11/17 20:11:35
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import logging as log
import sys
from typing import List, Tuple

from modules import url_entry
from modules.log_entry import extractLogEntry
from modules.url_entry import UrlEntry
from modules.url_match import UrlMatcher
from sql.db import DB as db
from sql.db import (ORIGIN_TABLE_LABELS, ORIGIN_TABLE_NAME,
                    URL_ENTRY_TABLE_LABELS, URL_ENTRY_TABLE_NAME)
from utils.file_utils import getFilesByPath
from utils.logger_utils import logInit

ORIGIN_LOG_LOCAL_PATH = '../../origindata'
# 本地原始日志的存放路径

LOG_FILE_SUFFIX = '.log'
# 原始日志文件的格式/后缀名


URL_ENTRY_LOCAL_PATH = "data/urls"
# 本地urlEntry的文件路径

URL_ENTRY_FILE_SUFFIX = '.urls'
# 本地urlEntry的后缀名


def uploadUrlEntryToDB():
    """
    uploadUrlEntryToDB 仅在第一次调用，适用于将本地urls文件中的 urlEntry 上传到数据库中
    """
    files = getFilesByPath(
        URL_ENTRY_LOCAL_PATH, URL_ENTRY_FILE_SUFFIX, [], [])
    for filename in files:
        log.info('开始处理%s' % filename)
        successCount, failCount = 0, 0
        with open(filename, 'r') as f:
            values = []
            for line in f:
                try:
                    entry = UrlEntry(line)
                    values.append(entry.getSet())
                    successCount += 1
                except Exception as e:
                    log.debug(e)
                    failCount += 1
        log.info('识别到%d条规则, 结构化成功:%d, 失败:%d' %
                 (successCount+failCount, successCount, failCount))
        try:
            db.insert(URL_ENTRY_TABLE_NAME, URL_ENTRY_TABLE_LABELS, values)
        except Exception as e:
            log.error(e)


def downloadUrlEntryFromDB() -> List[UrlEntry]:
    """
    downloadUrlEntryFromDB 从数据库中获取所有的Entry
    """
    try:
        entrySets = db.query(URL_ENTRY_TABLE_NAME, URL_ENTRY_TABLE_LABELS)
        entrys = []
        for entry in entrySets:
            entrys.append(UrlEntry(paraSet=entry))
        return entrys
    except Exception:
        return []


def getUrlEntryFromLocal() -> List[UrlEntry]:
    """
    getUrlEntryFromLocal 从本地获取 UrlsEntry
    Returns:
        List[UrlEntry]: 返回所有的 urlEntry
    """
    files = getFilesByPath(
        URL_ENTRY_LOCAL_PATH, URL_ENTRY_FILE_SUFFIX, [], [])
    entrys = []
    for filename in files:
        log.info('开始处理%s' % filename)
        successCount, failCount = 0, 0
        with open(filename, 'r') as f:
            for line in f:
                try:
                    entry = UrlEntry(line)
                    entrys.append(entry)
                    successCount += 1
                except Exception as e:
                    log.debug(e)
                    failCount += 1

        log.info('识别到%d条规则, 结构化成功:%d, 失败:%d' %
                 (successCount+failCount, successCount, failCount))
    return entrys


def uploadOriginLogsToDB():
    """
    readLogsAndUploadToDB 读取本地日志文件，并上传到数据库中
    """
    files = getFilesByPath(
        ORIGIN_LOG_LOCAL_PATH, LOG_FILE_SUFFIX, ['icaslog'], ['api', 'token'])

    # 生成 urlMatch 用于 url 归一化，如果抛出异常，则自动退出
    matcher = UrlMatcher(downloadUrlEntryFromDB())
    # url = '/fa/commoncore/assetCommonCore/remoteGetCurrenUserInfo'
    # print(matcher.convert(url, 'GET'))
    allSuccess, allFail = 0, 0
    for filename in files:
        log.info('开始处理%s' % filename)
        successCount, failCount = 0, 0
        with open(filename, 'r') as f:
            values = []
            for line in f:
                try:
                    value = extractLogEntry(line)
                    value.append(matcher.convert(value[4], value[5]))
                    log.debug("dirtyEntry: %s, urlEntry: %s" %
                              (value[4], value[15]))
                    values.append(tuple(value))
                    successCount += 1
                except Exception as e:
                    log.debug(e)
                    failCount += 1
            log.info('识别到%d条日志, 结构化成功:%d, 失败:%d' %
                     (successCount+failCount, successCount, failCount))
            allSuccess, allFail = allSuccess + successCount, allFail + failCount
            try:
                db.insert(ORIGIN_TABLE_NAME, ORIGIN_TABLE_LABELS, values)
            except Exception as e:
                log.error(e)

    log.info('共处理%d个文件，共计%d条日志，成功处理%d条，失败%d条' %
             (len(files), allSuccess + allFail, allSuccess, allFail))


if __name__ == '__main__':
    logInit(__file__, log.INFO, isStreaming=True)
    uploadOriginLogsToDB()
