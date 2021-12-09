'''
@File    :   logger_utils.py
@Time    :   2021/11/18 21:36:13
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import logging
from utils.file_utils import getPrefixName


def logInit(filename: str, level: int = logging.DEBUG, isStreaming=False):
    """
    logInit 对日志系统的初始化

    Args:
        filename (str): 本地化日志文件的名字
        level (int): 日志输出等级，默认为DEBUG
    """

    handlers = [
        # logging.StreamHandler(),
    ]
    if isStreaming:
        handlers.append(logging.StreamHandler())

    if len(filename) != 0:
        # 如果文件名不为空，则增加保存到本地的handler
        handlers.append(logging.FileHandler(
            getPrefixName(filename)+'.log', 'w', 'utf-8')
        )

    logging.basicConfig(
        level=level,
        format='[%(asctime)s][%(levelname)s]: %(message)s',
        handlers=handlers
    )
