'''
@File    :   log_parser.py
@Time    :   2021/08/18 14:15:45
@Author  :   Chengze Zhang 
@Contact :   chengze1996@gmail.com
@License :   Copyright (c) 2020 Chengze Zhang
'''

# here put the import lib
import os
import datetime

from tools.files import getFilesByPath


# config
LOGS_PATH = r'D:\Workspace\origindata\logs'
LOGS_FORMAT = '.log'


class HttpEvent(object):
    """
    log struct
    """

    def __init__(self, originLog: str):
        """
        init httpEvent
        :param originLog: raw data
        :param saveOriginData: whether save raw data
        """
        splits = originLog.split(" ")
        content = list()

        for s in splits:
            s = s.strip()
            if s == "":
                continue
            # content.append(s)
            content.append(s)

        # remove ERROR log and abnormal log
        if content[2] == "ERROR" or len(content) < 14:
            raise Exception("error log")
        try:
            tmpDate = "{0} {1}".format(content[0], content[1])
            # parse date string to datetime
            self.timestamp = datetime.datetime.strptime(
                tmpDate, '%Y-%m-%d %H:%M:%S,%f').timestamp()
        except Exception as identifier:
            raise Exception(identifier)

        self.threadId = content[7]
        self.institutionId = content[8]
        self.userId = content[9]
        self.url = content[10]
        self.method = content[11]
        self.statusCode = content[12]
        self.parameterType = content[13]
        self.parameterName = content[14]

        # select log version
        if "." in content[-1] and isNumber(content[-2]):
            # last pos is vpn ip

            self.vpnip = content[-1]
            self.port = content[-2]
            parameterValueEnd = len(content) - 6
        elif "." in content[-1]:
            # last pos is ip

            self.vpnip = "0"
            self.port = "0"
            parameterValueEnd = len(content) - 4
        else:
            # last pos is port

            self.vpnip = "0"
            self.port = content[-1]
            parameterValueEnd = len(content) - 5

        self.parameterValue = " ".join(content[15:parameterValueEnd+1])
        self.headers = content[parameterValueEnd+1]
        self.name = content[parameterValueEnd+2]
        self.ip = content[parameterValueEnd+3]

    def simplyPrint(self, sep):
        """
        supply a method to print all value.
        """
        return sep.join([
            str(self.timestamp),
            self.threadId,
            self.institutionId,
            self.userId,
            self.url,
            self.method,
            self.statusCode,
            self.parameterType,
            self.parameterName,
            self.parameterValue.replace(sep, ""),
            self.headers,
            self.name,
            self.ip,
            self.port,
            self.vpnip
        ])

    def getSet(self, sep):
        """
        Gets all valid data for the current instance in sequence.
        """
        return [
            self.timestamp,
            self.threadId,
            self.institutionId,
            self.userId,
            self.url,
            self.method,
            self.statusCode,
            self.parameterType,
            self.parameterName,
            self.parameterValue.replace(sep, ""),
            self.headers,
            self.name,
            self.ip,
            self.port,
            self.vpnip
        ]


def isNumber(s):
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


class Session(object):
    """
    emmmmmmmmmmmmmmmmm
    """

    def __init__(self, hes, ipLocation: bool):
        """
        docstring
        """
        self.userId = hes[0].userId
        self.name = hes[0].name
        self.institutionId = hes[0].institutionId
        self.urls = []
        timestamps = []
        self.citys = set()
        self.ips = set()
        for he in hes:
            timestamps.append(he.timestamp)
            self.urls.append(he.url),
            self.ips.add(he.ip)

        # Units are seconds
        self.startTime = timestamps[0]
        self.endTime = timestamps[-1]
        self.heNumber = len(self.urls)

        self.aveageHETime = sum([timestamps[i]-timestamps[i-1]
                                for i in range(1, len(timestamps))]) / self.heNumber

    def getSet(self):
        return [
            self.userId,
            self.name,
            self.institutionId,
            "-".join(self.urls),
            "-".join(self.ips),
            self.startTime,
            self.endTime,
            self.aveageHETime,
            self.heNumber,
            "-".join(self.citys)
        ]

    @staticmethod
    def generateSession(hes: pd.DataFrame, urlToIndex, threshold, ipLocation) -> list:
        """
        Used to divide sessions into separate sessions in an unordered pile of logs.
        """
        #########################################################
        # TODO: simply save the index of url, ip, and drop others.
        #########################################################

        sessions = []

        # read by line
        paths = []
        lastHeaderKey, lastHEDate = "", 0

        # sort by timestamp
        hes = hes.sort_values(by='timestamp')
        hes.url = hes.url.apply(lambda x: urlToIndex[x])

        for he in hes.itertuples():
            # if same operation
            if paths and he.url == paths[-1] and float(he.timestamp) - lastHEDate < 1:
                lastHEDate = he.timestamp
                continue

            #  get session key in headers
            headersJSON = json.loads(he.headers)
            flag = False
            for header in headersJSON:
                if header['value'] == lastHeaderKey:
                    lastHeaderKey = header['value']
                    flag = True

            if not flag and float(he.timestamp) - lastHEDate > threshold:
                # start a new session
                if paths:
                    session = Session(paths, ipLocation)
                    sessions.append(session.getSet())
                    # sessions.append("-".join([urlToIndex[url] for url in paths]))
                paths.clear()
                lastHeaderKey = headersJSON[0]['value']

            # update paths
            paths.append(he)
            lastHEDate = he.timestamp

        session = Session(paths, ipLocation)
        sessions.append(session.getSet())
        # sessions.append("-".join([urlToIndex[url] for url in paths]))
        return sessions
