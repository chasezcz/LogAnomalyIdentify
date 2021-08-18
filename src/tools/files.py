'''
@File    :   files.py
@Time    :   2021/08/18 14:25:04
@Author  :   Chengze Zhang 
@Contact :   chengze1996@gmail.com
@License :   Copyright (c) 2020 Chengze Zhang
'''

# here put the import lib
import os
from typing import List


def getFilesByPath(path: str, format: str) -> List:
    """
    Gets all files under the specified path
    :param path: specific path
    :return: absolute path list for all files
    """
    allfiles = list()
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(format):
                allfiles.append(os.path.join(root, f))
    return allfiles
