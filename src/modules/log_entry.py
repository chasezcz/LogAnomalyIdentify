
'''
@File    :   log_entry.py
@Time    :   2021/11/17 14:53:02
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import datetime
from typing import List

from utils.str_utils import isIPAddress


def extractLogEntry(s: str) -> List:
    """
    extractLogEntry 将单条日志转化为 符合 ORIGIN_TABLE_LABLES 的元组

    Raises:
        Exception: 转换失败，抛出异常

    Args:
        s (str): 输入日志文本行

    Returns:
        List: 返回列表
    """
    content = s.split()
    try:
        time = datetime.datetime.strptime(
            content[0]+" "+content[1], "%Y-%m-%d %H:%M:%S,%f").timestamp()
        level = content[2]
        if (level == "ERROR"):
            raise Exception("error level log. continue")
        threadID = content[7].strip()
        institutionID = content[8].strip()
        userID = content[9].strip()
        url = content[10].strip().replace(',', '')
        method = content[11].strip()
        statusCode = content[12].strip()
        parameterType = content[13].strip().replace(' ', '').replace('\t', '')
        parameterName = content[14].strip().replace(' ', '').replace('\t', '')
        parameterValue = content[15].strip().replace(' ', '').replace('\t', '')
        idx = 16
        while (idx+2 < len(content) and not isIPAddress(content[idx+2])):
            parameterValue += content[idx]
            idx += 1
        headers = content[idx]
        name = content[idx+1]
        ip = content[idx+2]
        port, vpnip = "", ""
        if (idx+3 < len(content)):
            port = content[idx+3]
        if (idx+4 < len(content)):
            vpnip = content[idx+4]

        # 处理部分空字段
        emptyList = '[]'
        emptyString = ''
        parameterType = emptyString if parameterType == emptyList else parameterType
        parameterName = emptyString if parameterName == emptyList else parameterName
        parameterValue = emptyString if parameterValue == emptyList else parameterValue

        return [
            time,
            threadID,
            institutionID,
            userID,
            url,
            method,
            statusCode,
            parameterType,
            parameterName,
            parameterValue,
            headers,
            name,
            ip,
            port,
            vpnip
        ]
    except Exception as e:
        raise Exception("failed because to %s" % str(e))


if __name__ == '__main__':
    filePath = "/home/chase/Workspace/origindata/logs/audit/fin/icaslog.log_2020-11-06.log"
    data = dict()

    count = 0
    with open(filePath, 'r', encoding='utf-8') as f:
        # read raw log by line.
        for line in f:
            try:
                # from sql import db

                res = extractLogEntry(line)
                # db.DB.insert('origin', db.ORIGIN_TABLE_LABELS, [res])
                # print(extractLogEntry(line))
                name = res[12]
                data[len(name)] = name
                # break
            except Exception as e:
                # print(e)

                pass

    for (key, value) in data.items():
        print('%s: %s' % (key, value))
