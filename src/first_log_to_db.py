'''
@File    :   first_log_to_db.py
@Time    :   2021/11/17 20:11:35
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

# 第一步，将日志文件进行初步处理，存储到数据库中
import logging as log
import os
import sys
import time
import datetime

from modules.log_entry import extractLogEntry
from utils.file_utils import getFilesByPath
from sql.db import DB as db, ORIGIN_TABLE_LABELS

log.basicConfig(
    format='[%(asctime)s][%(levelname)s]: %(message)s',
    level=log.INFO,
    filename='first_log_to_db.log',
    filemode='w',
)


if __name__ == '__main__':
    files = getFilesByPath(
        '/home/chase/Workspace/origindata/', 'log', [], ['api', 'token'])

    allSuccess, allFail = 0, 0
    for filename in files:
        log.info('开始处理%s' % filename)
        successCount, failCount = 0, 0
        with open(filename, 'r') as f:
            values = []
            for line in f:
                try:
                    val = extractLogEntry(line)
                    values.append(val)
                    successCount += 1
                except Exception as e:
                    log.debug(e)
                    failCount += 1
            log.info('识别到%d条日志, 结构化成功:%d, 失败:%d' %
                     (successCount+failCount, successCount, failCount))
            allSuccess, allFail = allSuccess + successCount, allFail + failCount
            try:
                db.insertOrigin(values)
            except Exception as e:
                log.error(e)

    log.info('共处理%d个文件，共计%d条日志，成功处理%d条，失败%d条' %
             (len(files), allSuccess + allFail, allSuccess, allFail))
