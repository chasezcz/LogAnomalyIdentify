'''
@File    :   resorter.py
@Time    :   2021/12/14 15:22:27
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


from modules.log_entry import extractLogEntry
from upload_data_to_db import LOG_FILE_SUFFIX, ORIGIN_LOG_LOCAL_PATH
from utils.file_utils import getFilesByPath, writeList
import logging as log


def resortLogByUserID(inputPath: str, outputPath: str):
    """
    resortLogByUserID 将日志文件 按照userID 进行切分，在单个文件中，按照时间进行排序

    Args:
        dataPath (str): 输入路径
        targetPath (str): 输出路径
    """
    files = getFilesByPath(
        inputPath, LOG_FILE_SUFFIX, [], ['api', 'token'])

    for filename in files:
        users = {}
        with open(filename, 'r') as f:
            for line in f:
                try:
                    value = extractLogEntry(line)
                    userID = value[3]
                    if userID not in users:
                        users[userID] = []
                    users[userID].append(line)
                except Exception as e:
                    log.debug('转换失败: {}, {}'.format(line, e))
        for userID, lines in users.items():
            writeList(outputPath+'/'+str(userID)+'.log', lines, True)
    log.debug("转换完成，开始重排序")

    # files = getFilesByPath(outputPath, LOG_FILE_SUFFIX, [], [])
    # log.debug("识别到{}个用户".format(len(files)))
    # for filename in files:
    #     values = []
    #     with open(filename, 'r') as f:
    #         for line in f:
    #             value = extractLogEntry(line)
    #             values.append(value)
    #     values.sort(key=)
