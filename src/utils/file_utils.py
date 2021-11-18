'''
@File    :   file_utils.py
@Time    :   2021/11/17 20:06:34
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


# here put the import lib
import os
from typing import List


def getFilesByPath(path: str, formats: List[str], includeKeys: List[str], ignoreKeys: List[str]) -> List[str]:
    """
    getFilesByPath      Gets all files under the specified path.

    Args:
        path (str): 目录的路径
        formats (List[str]): 想要获取文件的后缀名
        includeKeys (List[str]): 文件名中包含的关键字，若为空，则全部获取
        ignoreKeys (List[str]): 文件名中不可以包含的关键字，若为空，则全部获取
    Returns:
        List[str]: 所有目标文件的绝对路径 
    """

    allfiles = list()
    for root, _, files in os.walk(path):
        for f in files:
            format = f.split('.')[-1]
            if format not in formats:
                continue
            # ignore keys judge
            isIgnore = False
            for key in ignoreKeys:
                if key in f:
                    isIgnore = True
                    break
            if isIgnore:
                continue
            # include keys judge
            isIgnore = True
            for key in includeKeys:
                if key in f:
                    isIgnore = False
                    break
            if not isIgnore or len(includeKeys) == 0:
                allfiles.append(os.path.join(root, f))
    return allfiles


def getPrefixName(filename: str) -> str:
    """
    getPrefixName 找到文件（路径）的文件前缀名（不包含后缀名）

    Args:
        filename (str): 文件名或文件路径

    Returns:
        str: 文件前缀名
    """
    try:
        name = filename.split('/')[-1]
        return name.split('.')[0]
    except Exception:
        return ""


def getSuffixName(filename: str) -> str:
    """
    getSuffix 获取文件的后缀名

    Args:
        filename (str): 文件名

    Returns:
        str: 后缀名
    """
    try:
        name = filename.split('.')[-1]
        return name
    except Exception:
        return ""
