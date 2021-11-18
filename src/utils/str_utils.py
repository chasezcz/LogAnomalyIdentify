'''
@File    :   str_utils.py
@Time    :   2021/11/17 20:06:24
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''


def isNumber(s: str) -> bool:
    """
    isNumber 判断字符串是否为数字

    Args:
        s (str): 字符串

    Returns:
        bool: 判断结果
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def isIPAddress(s: str) -> bool:
    """
    isIPAddress 判断字符串 s 是否为一个合法的ip地址

    Args:
        s (str): 输入的 ip 字符串

    Returns:
        bool: 判断结果
    """
    s.strip()
    ss = s.split('.')
    if (len(ss) != 4):
        return False
    try:
        a, b, c, d = int(ss[0]), int(ss[1]), int(ss[2]), int(ss[3])

        def f(i):
            return i >= 0 and i <= 255

        return f(a) and f(b) and f(c) and f(d)
    except Exception:
        return False


if __name__ == '__main__':
    ip = "125.150.16.0"
    print(isIPAddress(ip))
