import argparse
import logging as log
import os

import torch

from modules.lstm import train
from utils.logger_utils import logInit

torch.manual_seed(0)

if __name__ == '__main__':
    logInit(__file__, log.DEBUG, isStreaming=True)
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--epochs', type=int, default=50, metavar='N',
                        help='number of epochs to train (default: 50)')
    parser.add_argument('--window-size', type=int, default=10, metavar='N',
                        help='length of training window (default: 10)')
    parser.add_argument('--input-size', type=int, default=1, metavar='N',
                        help='model input size (default: 1)')
    parser.add_argument('--hidden-size', type=int, default=64, metavar='N',
                        help='hidden layer size (default: 64)')
    parser.add_argument('--num-layers', type=int, default=2, metavar='N',
                        help='number of model\'s layer (default: 2)')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')

    parser.add_argument('--num-classes', type=int, metavar='N',
                        help='the number of model\'s output, must same as pattern size!')
    parser.add_argument('--num-candidates', type=int, metavar='N',
                        help='the number of predictors sequences as correct predict.')

    # Pass container environment
    parser.add_argument('--hosts', type=list, default=['127.0.0.1'],
                        help='args for SageMaker distributed training.')
    parser.add_argument('--current-host', type=str, default='127.0.0.1',
                        help='args for SageMaker distributed training.')
    parser.add_argument('--model-dir', type=str, default='./model/',
                        help='the place where to store the model parameter.')
    parser.add_argument('--data_dir', type=str, default='./data/10_30',
                        help='the place where to store the training data.')
    parser.add_argument('--num-gpus', type=int, default=0,
                        help='number of gpu to train')

    # Local mode
    parser.add_argument('--local', type=bool, default=False,
                        help='local training model.')

    if not os.path.isdir('model/'):
        os.mkdir('model/')
    train(parser.parse_args())
