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
