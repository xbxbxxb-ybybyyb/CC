# coding: utf-8
# Author：fengchi863
# Date ：2022/3/23 13:49

from SimiStock.Script.backtest_1method20220329 import backtest_1method
from SimiStock.SimiStockGenerator.util import util
from itertools import product
import pandas as pd
from SimiStock.config.path_config import *

# hedge生成参数
param_dict = {'method_name': ['叠加风格'],
              'concept': ['SW1'],
              'pre_days_num': [120],
              'hedge_max_num': [12],
              'corr_threshold': [0.7, 0.65, 0.6, 0.5],
              'weight_kind': ['v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7']}


# 回测参数
duration = 120
hedge_num = 20

if __name__ == '__main__':
    param_list = list(product(param_dict['method_name'], param_dict['concept'], param_dict['pre_days_num'],
                               param_dict['hedge_max_num'], param_dict['corr_threshold'], param_dict['weight_kind']))

    output_names = list()
    for param in param_list:
        hedge_param_list = [param[0], str(param[3]), str(param[4]), param[5]]
        bt_param_list = [str(param[3]), str(param[4]), param[5]]
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
        stats_df = pd.read_excel(other_stats_path + f'stats_{output_name}', sheet_name=['汇总'], index_col=0)['汇总']
        for col in stats_df.index:
            df[col] = stats_df[0][col]
        summary = pd.concat([summary, df], axis=0)

    util.save_df2xls(summary, bt_summary_path, f'final_summary_测试风格方案.xlsx')