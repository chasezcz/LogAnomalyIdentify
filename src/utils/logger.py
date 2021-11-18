'''
@File    :   logger.py
@Time    :   2021/11/18 16:22:09
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


import logging
from utils.file_utils import getPrefixName


def logInit(filename: str, level: int = logging.DEBUG):
    """
    logInit 对日志系统的初始化

    Args:
        filename (str): 本地化日志文件的名字
        level (int): 日志输出等级，默认为DEBUG
    """
    if (len(filename) == 0):
        logging.basicConfig(
            format='[%(asctime)s][%(levelname)s]: %(message)s',
            level=level,
        )
    else:
        logging.basicConfig(
            format='[%(asctime)s][%(levelname)s]: %(message)s',
            level=level,
            filename=getPrefixName(filename) + '.log',
            filemode='w',
        )
