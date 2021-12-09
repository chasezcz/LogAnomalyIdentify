'''
@File    :   lstm.py
@Time    :   2021/11/19 22:18:16
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import argparse
import json
import logging as log
import os
import random
from pathlib import WindowsPath

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # 定义网络结构为，LSTTM 后 跟一个 全连接层 full-  layer
        self.lstm = nn.LSTM(input_size,
                            hidden_size,
                            num_layers,
                            batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, input):
        h0 = torch.zeros(self.num_layers, input.size(0),
                         self.hidden_size).to(input.device)
        c0 = torch.zeros(self.num_layers, input.size(0),
                         self.hidden_size).to(input.device)
        out, _ = self.lstm(input, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


def generate(name, window_size):
    num_sessions = 0
    inputs = []
    outputs = []

    with open(name, 'r') as f:
        line = f.readline()
        while line:
            line = tuple(
                map(lambda n: n - 1, map(int, line.strip().split())))
            for i in range(len(line) - window_size):
                inputs.append(line[i:i + window_size])
                outputs.append(line[i + window_size])
            line = f.readline()
            num_sessions += 1
    log.info('Number of session({}): {}'.format(name, len(inputs)))
    log.info('Number of seqs({}): {}'.format(name, len(inputs)))
    dataset = TensorDataset(torch.tensor(inputs, dtype=torch.float),
                            torch.tensor(outputs))
    return dataset


def train(args):
    # 判断可用的gpu数量
    if args.num_gpus > 0 and not torch.cuda.is_available():
        log.warning(
            "No CUDA available, setting num_gpus to 0 (num_gpus = {}).".format(
                args.num_gpus))
        args.num_gpus = 0

    # 判断是否使用GPU
    use_cuda = args.num_gpus > 0
    log.debug("Number of gpus requested - {}, available - {}.".format(
        args.num_gpus, torch.cuda.device_count()))
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}
    device = torch.device("cuda" if use_cuda else "cpu")

    # set the seed for generating random numbers，设置随机种子
    torch.manual_seed(args.seed)
    if use_cuda:
        log.info('Use CUDA')
        torch.cuda.manual_seed(args.seed)
    log.info(device)
    # 获取训练数据
    log.info("Get train data loader")
    trainDataset = generate(name='%s/train' % args.data_dir,
                            window_size=args.window_size)
    trainDataLoader = DataLoader(
        trainDataset, batch_size=args.batch_size, **kwargs)

    # 获取验证集数据
    validationDataset = []
    with open('%s/validation' % args.data_dir, 'r') as f:
        for line in f.readlines():
            line = list(map(lambda n: n - 1, map(int, line.strip().split())))
            validationDataset.append(line)

    log.debug("Processes {}/{} ({:.0f}%) of train data".format(
        len(trainDataLoader.sampler), len(trainDataLoader.dataset),
        100. * len(trainDataLoader.sampler) / len(trainDataLoader.dataset)))

    # 获取网络模型并进行部署
    model = Model(args.input_size, args.hidden_size, args.num_layers,
                  args.num_classes).to(device)

    # 交叉熵
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    for epoch in range(1, args.epochs + 1):
        # 迭代训练
        log.debug("Start train epoch %d" % epoch)
        model.train()
        trainLoss = 0
        for seq, label in trainDataLoader:
            seq = seq.clone().detach().view(-1, args.window_size,
                                            args.input_size).to(device)
            optimizer.zero_grad()
            output = model(seq)
            # log.debug(output.shape)
            loss = criterion(output, label.to(device))
            loss.backward()
            optimizer.step()
            # 计算交叉熵loss
            trainLoss += loss.item()
        log.debug('Epoch [{}/{}], Train_loss: {}'.format(
            epoch, args.epochs,
            round(trainLoss / len(trainDataLoader.dataset), 4)))

        if epoch % 10 == 0:
            # eval
            log.debug("start eval")
            predict_cnt = 0
            nomaly_cnt = 0
            for line in random.sample(validationDataset, 500):
                cnt = 0
                for i in range(len(line) - args.window_size):
                    seq = line[i: i + args.window_size]
                    label = line[i + args.window_size]

                    seq = torch.tensor(seq, dtype=torch.float).view(
                        -1, args.window_size, args.input_size).to(device)
                    label = torch.tensor(label).view(-1).to(device)
                    output = model(seq)
                    predict = torch.argsort(output, 1)[
                        0][-args.num_candidates:]

                    if label in predict:
                        cnt += 1

                if cnt >= (len(line)-args.window_size) * 0.9:
                    nomaly_cnt += 1
                predict_cnt += 1

            log.debug('save model, checkpoint. acc : {}'.format(
                      (round(nomaly_cnt / predict_cnt, 4))))
            save_model(model, 'model%d' % epoch, args.model_dir, args)
            model.cuda()

    log.debug('Finished Training')
    save_model(model, 'model', args.model_dir, args)


def save_model(model, name, model_dir, args):
    log.info("Saving the model.")
    path = os.path.join(model_dir, '%s.pth' % name)
    torch.save(model.cpu().state_dict(), path)
    # Save arguments used to create model for restoring the model later
    model_info_path = os.path.join(model_dir, '%s_info.pth' % name)
    with open(model_info_path, 'wb') as f:
        model_info = {
            'input_size': args.input_size,
            'hidden_size': args.hidden_size,
            'num_layers': args.num_layers,
            'num_classes': args.num_classes,
            'num_candidates': args.num_candidates,
            'window_size': args.window_size,
        }
        torch.save(model_info, f)


def model_fn(model_dir):
    log.info('Loading the model.')
    model_info = {}
    with open(os.path.join(model_dir, 'model_info.pth'), 'rb') as f:
        model_info = torch.load(f)
    log.debug('model_info: {}'.format(model_info))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info('Current device: {}'.format(device))
    model = Model(input_size=model_info['input_size'],
                  hidden_size=model_info['hidden_size'],
                  num_layers=model_info['num_layers'],
                  num_classes=model_info['num_classes'])
    with open(os.path.join(model_dir, 'model.pth'), 'rb') as f:
        model.load_state_dict(torch.load(f))
    input_size = model_info['input_size']
    window_size = model_info['window_size']
    num_candidates = model_info['num_candidates']
    return {
        'model': model.to(device),
        'window_size': window_size,
        'input_size': input_size,
        'num_candidates': num_candidates
    }


def input_fn(request_body, request_content_type):
    log.info('Deserializing the input data.')
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(
            "{} not supported by script!".format(request_content_type))


def predict_fn(input_data, model_info):
    log.info('Predict next template on this pattern series.')
    line = input_data['line']
    num_candidates = model_info['num_candidates']
    input_size = model_info['input_size']
    window_size = model_info['window_size']
    model = model_info['model']

    log.info(line)
    log.debug(num_candidates)
    log.debug(input_size)
    log.debug(window_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.debug('Current device: {}'.format(device))

    predict_cnt = 0
    anomaly_cnt = 0
    predict_list = [0] * len(line)
    for i in range(len(line) - window_size):
        seq = line[i:i + window_size]
        label = line[i + window_size]
        seq = torch.tensor(seq,
                           dtype=torch.float).view(-1, window_size,
                                                   input_size).to(device)
        label = torch.tensor(label).view(-1).to(device)
        output = model(seq)
        predict = torch.argsort(output, 1)[0][-num_candidates:]
        if label not in predict:
            anomaly_cnt += 1
            predict_list[i + window_size] = 1
        predict_cnt += 1
    return {
        'anomaly_cnt': anomaly_cnt,
        'predict_cnt': predict_cnt,
        'predict_list': predict_list
    }


def output_fn(prediction, accept):
    log.info('Serializing the generated output.')
    if accept == "application/json":
        return json.dumps(prediction), accept
    raise ValueError(
        "{} accept type is not supported by this script".format(accept))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument('--batch-size',
                        type=int,
                        default=64,
                        metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--epochs',
                        type=int,
                        default=50,
                        metavar='N',
                        help='number of epochs to train (default: 50)')
    parser.add_argument('--window-size',
                        type=int,
                        default=10,
                        metavar='N',
                        help='length of training window (default: 10)')
    parser.add_argument('--input-size',
                        type=int,
                        default=1,
                        metavar='N',
                        help='model input size (default: 1)')
    parser.add_argument('--hidden-size',
                        type=int,
                        default=64,
                        metavar='N',
                        help='hidden layer size (default: 64)')
    parser.add_argument('--num-layers',
                        type=int,
                        default=2,
                        metavar='N',
                        help='number of model\'s layer (default: 2)')
    parser.add_argument('--seed',
                        type=int,
                        default=1,
                        metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument(
        '--backend',
        type=str,
        default=None,
        help='backend for distributed training ' +
        '(tcp, gloo on cpu and gloo, nccl on gpu)'
    )

    parser.add_argument(
        '--num-classes',
        type=int,
        metavar='N',
        help='the number of model\'s output, must same as pattern size!')
    parser.add_argument(
        '--num-candidates',
        type=int,
        metavar='N',
        help='the number of predictors sequences as correct predict.')

    # parser.add_argument('--model-dir',
    #                     type=str,
    #                     default='')
    parser.add_argument('--data-dir',
                        type=str,
                        default='data/')
    parser.add_argument('--num-gpus',
                        type=int,
                        default=os.environ['SM_NUM_GPUS'])

    train(parser.parse_args())
