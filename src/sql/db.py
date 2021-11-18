'''
@File    :   sql.py
@Time    :   2021/11/17 15:44:19
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''
from datetime import datetime
from typing import List, Tuple

import mysql.connector

# origin 表的表头
ORIGIN_TABLE_LABELS = [
    "time",
    "threadID",
    "institutionID",
    "userID",
    "url",
    "method",
    "statusCode",
    "parameterType",
    "parameterName",
    "parameterValue",
    "headers",
    "name",
    "ip",
    "port",
    "vpnIP"
]


class Database():
    """
    Database 封装Mysql数据库的基本功能
    """

    def __init__(self) -> None:
        """
        __init__ 数据库初始化
        """
        self.__conn = mysql.connector.connect(user='root',
                                              database='arplogs',
                                              password='Arp@2020',
                                              host='localhost')
        self.__cursor = self.__conn.cursor()

    def __del__(self):
        """
        __del__ 析构函数，关闭数据库连接接口
        """
        self.__conn.close()

    def __generateInsertSQL(self, table: str, columns: List[str]) -> str:
        return "INSERT INTO %s %s VALUES %s" % (
            table,
            '(' + ','.join(columns) + ')',
            '(' + ','.join(['%s' for i in range(len(columns))]) + ')'
        )

    def __generateQuerySQL(self, table: str, columns: List[str]) -> str:
        return "SELECT %s FROM %s" % (','.join(columns), table)

    def query(self, table: str, columns: List[str]):
        sql = self.__generateQuerySQL(table, columns)
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def insert(self, table: str, columns: List[str], values: List[Tuple]):
        """
        insert 向数据库中插入多条数据

        Args:
            table (str): 数据表名称
            columns (List[str]): 数据表中插入的列名
            values (List[Tuple]): 数据表中插入的值，每一组是一个Tuple，共多组
        """
        if len(values) == 0:
            return
        sql = self.__generateInsertSQL(table, columns)
        self.__cursor.executemany(sql, values)
        self.__conn.commit()

    def insertOrigin(self, values: List[Tuple]):
        """
        insert 向数据库中插入多条数据

        Args:
            table (str): 数据表名称
            columns (List[str]): 数据表中插入的列名
            values (List[Tuple]): 数据表中插入的值，每一组是一个Tuple，共多组
        """
        if len(values) == 0:
            return
        timestamp = values[0][0]
        dt = datetime.fromtimestamp(timestamp)
        table = 'origin_%d_%s' % (dt.year, 'head' if dt.month < 7 else 'tail')
        # print(table)
        self.insert(table, ORIGIN_TABLE_LABELS, values)


DB = Database()


if __name__ == '__main__':
    values = [
        (1629089285.177, '8616', '17311', '17311-101520', '/fa/commoncore/assetCommonCore/remoteGetCurrenUserInfo', 'GET', '200', '', '', '',
         '[{"httpOnly":false,"maxAge":-1,"name":"Authorization","secure":false,"value":"efWLb4U4xgrna2om","version":0}]', '郭x阳', '123.119.45.229', '22514', '192.168.177.191'),
    ]
    DB.insertOrigin(values)
