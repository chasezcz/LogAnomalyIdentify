'''
@File    :   url_entry.py
@Time    :   2021/11/18 20:30:58
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import re
from typing import Tuple


class UrlEntry(object):
    """
    UrlEntry 表示一个完整url规则，其中包括 
    1. 模块名 module
    2. HTTP方法 method
    3. url路径 url 
    4. url中子路径的数量 length 
    5. pattern 正则的编译pattern，方便后续进行快速计算
    """

    def __init__(self, origin: str = "", paraSet: Tuple = None) -> None:
        """
        __init__ 初始化函数

        Args:
            origin (str): urls文件中的单行文本
            paraSet (Tuple): 从数据库中获取到的信息元组，将元组重新封装为一个UrlEntry
        """
        if (len(origin) > 0):
            ss = origin.split()
            self.module = ss[0]
            self.method = ss[1]
            self.url = '/' + ss[2].strip('/')
        elif (len(paraSet) == 3):
            self.module = paraSet[0]
            self.method = paraSet[1]
            self.url = paraSet[2]
        else:
            raise Exception('传入参数信息不足，构建urlEntry失败, %s' % origin)

        self.length = len(self.url.split("/"))
        pattern = re.sub(r'\{[^/]{1,100}\}',
                         r'[^/]{2,100}', self.url, count=100)

        self.pattern = re.compile(pattern)

    def getSet(self):
        """
        getSet 获取必要信息

        Returns:
            [type]: 以 元组 形式返回
        """
        return (
            self.module,
            self.method,
            self.url,
        )

    def isMatch(self, dirtyEntry: str) -> bool:
        """
        isMatch 测试与目标url是否相匹配

        Args:
            dirtyEntry (str): 目标url，未经归一化的url

        Returns:
            bool: 判断结果，True/False
        """
        if re.match(self.pattern, dirtyEntry) != None:
            return True
        return False


if __name__ == '__main__':
    entry = UrlEntry("fin GET /fin/arBillAssembly/getOrgInfo/{deptId}")
    urls = [
        "/fin/arBillAssembly/getOrgInfo/aijfeiowejf",
        "/fin/arBillAssembly/getOrgIno/aijfeiowejf/",
        "/fin/arBillAssembly/getOrgInfo/aijfeiowejf/wef",
    ]
    for url in urls:
        print(entry.isMatch(url))
