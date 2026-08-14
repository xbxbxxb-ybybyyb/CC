# coding: utf-8
# Author：fengchi863
# Date ：2022/3/10 16:45

from Script.backtest_1method import backtest_1method
from SimiStock.SimiStockGenerator.util import util
from itertools import product
import pandas as pd
from SimiStock.config.path_config import *

# hedge生成参数
param_dict1 = {'method_name': ['日频pctchg相关性', '日频close相关性', '日频pctchg对数相关性'],
               'concept': ['SW1', 'SW2', 'SW3', 'allMarket'],
               'pre_days_num': ['120', '240']}

param_dict2 = {'method_name': ['5分钟close相关性'],
               'concept': ['SW1', 'SW2', 'SW3', 'allMarket'],
               'pre_days_num': ['60', '120']}

# 回测参数
duration = 120
hedge_num = 14

if __name__ == '__main__':
    param_list1 = list(product(param_dict1['method_name'], param_dict1['concept'], param_dict1['pre_days_num']))
    param_list2 = list(product(param_dict2['method_name'], param_dict2['concept'], param_dict2['pre_days_num']))

    output_names = list()
    for param in param_list1:
        hedge_param_list = [param[0], param[1], str(param[2])]
        bt_param_list = [param[0], param[1], str(param[2]), str(duration), str(hedge_num)]
        filename = '_'.join(hedge_param_list) + '_result.pkl'
        output_name = '_'.join(bt_param_list) + '_bt_summary.xlsx'
        output_names.append(output_name)
        backtest_1method(filename=filename,
                         output_name=output_name,
                         mode='multi',
                         kernal_num=24,
                         duration=duration,
                         hedge_num=hedge_num,
                         method_name=param[0])

    for param in param_list2:
        hedge_param_list = [param[0], param[1], str(param[2])]
        bt_param_list = [param[0], param[1], str(param[2]), str(duration), str(hedge_num)]
        filename = '_'.join(hedge_param_list) + '_result.pkl'
        output_name = '_'.join(bt_param_list) + '_bt_summary.xlsx'
        output_names.append(output_name)
        backtest_1method(filename=filename,
                         output_name=output_name,
                         mode='multi',
                         kernal_num=24,
                         duration=duration,
                         hedge_num=hedge_num,
                         method_name=param[0])

    print('已全部回测完成')
    summary = pd.DataFrame()
    for output_name in output_names:
        df = pd.read_excel(bt_path + output_name)
        summary = pd.concat([summary, df], axis=0)

    util.save_df2xls(summary, bt_summary_path, f'final_summary20220327叠加相关性测试_{hedge_num}.xlsx')


