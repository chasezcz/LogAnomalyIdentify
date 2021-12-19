'''
@File    :   predict.py
@Time    :   2021/12/09 14:04:04
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import argparse
import json
import logging as log
from datetime import datetime

from tqdm import tqdm

from modules.lstm import input_fn, model_fn, predict_fn
from utils.logger_utils import logInit


def predict(args):
    model_info = model_fn(args.model_dir)

    log.debug("start eval")

    predict_cnt = 0
    nomaly_cnt = 0

    with open('%s/test' % args.data_dir, 'r') as f:
        content = f.readlines()
        for i in tqdm(range(len(content))):
            ss = content[i].strip().split()
            starttime = datetime.strptime(' '.join(ss[:2]), '%Y-%m-%d %H:%M:%S')
            userId = ss[2]
            line = list(map(lambda n: n - 1, map(int, ss[3:])))
            request = json.dumps({'line': line})
            input_data = input_fn(request, 'application/json')
            response = predict_fn(input_data, model_info)

            # res.append(response)
            predict_cnt += 1
            if response['predictCnt'] * 0.1 > response['anomalyCnt'] or len(response['result']) == 0: 
                nomaly_cnt += 1
            else:
                log.error("用户: {} 在 {} 存在风险行为，风险序列为: {}".format(
                    userId,
                    starttime,
                    ', '.join(['{}:{}'.format(key, value) for key, value in response['result'].items()])))

    log.info('nomaly_cnt: {}, predict_cnt: {},  acc : {}'.format(
        nomaly_cnt, predict_cnt,
        (round(nomaly_cnt / predict_cnt, 5))))


if __name__ == '__main__':
    logInit(__file__, log.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default='./model/',
                        help='the place where to store the model parameter.')
    parser.add_argument('--data_dir', type=str, default='./data/10_30',
                        help='the place where to store the training data.')
    args = parser.parse_args()
    predict(args)
