# coding: utf-8
# Author：fengchi863
# Date ：2022/6/29 16:56

import pandas as pd

log_floder_path = '/data/user/015614/AWorkHandOver/HANXU/Timing/hyper_param_search/log/'
log_file_name = 'hyper_opt_search20220627XGB400.log'

abs_file_path = log_floder_path + log_file_name

record_list = []
for line in open(abs_file_path, 'r', encoding='UTF-8'):
    if '此轮耗时' in line:
        res = line.split(':')
        mae, mse, total_profit, per_profit = eval(res[1])
        record_list.append([mae, mse, total_profit, per_profit])

record_df = pd.DataFrame(record_list, columns=['MAE', 'MSE', '总收益', '单笔收益'])
corr = record_df.corr()     # 计算几个变量间的相关性
"""
MAE与MSE之间相关性：肯定很高
MSE与总收益的相关性：是否有相关性
总收益与单笔收益的相关性：是否有相关性
"""
