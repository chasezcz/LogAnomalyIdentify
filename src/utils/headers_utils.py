'''
@File    :   headers_utils.py
@Time    :   2021/11/19 15:15:58
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


from typing import Dict, List


class Header:
    httpOnly = bool
    maxAge = int
    name = str
    secure = bool
    value = str
    version = int


def parseHeaders(origin: str) -> List[Dict]:
    """
    parseHeaders 从 日志headers字段中，解析header的头信息

    Args:
        origin (str): 原始信息，例如 '[{"httpOnly":false,"maxAge":-1,"name":"fine_remember_login","secure":false,"value":"-1","version":0}]'
    """
    # origin = '{' + origin[1:-1] + '}'
    if (len(origin) == 0):
        return []
    headers = json.loads(origin)
    return headers


def parseSessionIDFromHeaders(origin: str) -> List[str]:
    """
    parseSessionIDFromHeaders 从日志字段中，解析出sessionID

    Args:
        origin (str): 原始信息

    Returns:
        List[str]: sessionID 的列表
    """
    headers = parseHeaders(origin)
    sessionIDs = [header['value'] for header in headers]
    return sessionIDs


if __name__ == '__main__':
    import json
    sample = '[{"httpOnly":false,"maxAge":-1,"name":"Authorization","secure":false,"value":"aMlS7AD6HX9w","version":0},{"httpOnly":false,"maxAge":-1,"name":"fine_auth_token","secure":false,"value":"eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJmYW5ydWFuIiwiaWF0IjoxNTg2MjI2NTc1LCJleHAiOjE1ODYyMzAxNzUsInN1YiI6IjE3MzIxMS0xNTA4NSIsImRlc2NyaXB0aW9uIjoiWzk2NDhdWzRlYWVdKDE3MzIxMS0xNTA4NSkiLCJqdGkiOiJqd3QifQ.Z5NvuDG1DO4j5QvqFpM9v2nAMJGJki5wQkC7K5LvZcY","version":0},{"httpOnly":false,"maxAge":-1,"name":"fine_remember_login","secure":false,"value":"-1","version":0}]'
    print(parseSessionIDFromHeaders(sample))
