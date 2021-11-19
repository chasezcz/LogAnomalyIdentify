'''
@File    :   lstm.py
@Time    :   2021/11/19 22:18:16
@Author  :   Chengze Zhang
@Contact :   929160190@qq.com
'''

import torch
import torch.nn as nn


class Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
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
