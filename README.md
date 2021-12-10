# LogAnomalyIdentify

基于日志的异常分析检测

## 数据处理

log parser

`<module> <url> <method> <parameterName>`

使用 threshold 作为日志分割，当两条日志拥有相同的 userID，且 ip 两者时间差 小于 threshold 时，作为一个序列进行使用

## 2. 异常定义及如何制作异常数据

在异常分析中，首先要定义异常，何为异常。本实验中统计了常见异常，如下所示，并分别制定方案去识别。

1. 短时间大量访问
2. 机器爬取
3. 有异地登陆风险的
4. 行为模式异常
5. 越权访问

## 3. 模型设计

训练：
`python src/train.py --num-class 3984 --num-candidates 398 --epochs 200 --window-size 5 --num-gpus 1 --hidden-size 128 --num-layers 4 --data_dir=./data/200_30 --model-dir=./model/200_5_128_4`

测试：
`python src/predict.py --data_dir=./data/200_30 --model-dir=./model`
train cost: 1m30s / epoch
eval cost :
