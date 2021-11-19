# LogAnomalyIdentify

基于日志的异常分析检测

## 数据处理

log parser

`<module> <url> <method> <parameterName>`

使用 threshold 作为日志分割，当两条日志拥有相同的 userID，且 ip 两者时间差 小于 threshold 时，作为一个序列进行使用
