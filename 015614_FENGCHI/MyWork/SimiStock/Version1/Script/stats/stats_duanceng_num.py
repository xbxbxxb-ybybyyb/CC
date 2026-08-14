# coding: utf-8
# Author：fengchi863
# Date ：2022/4/6 13:43

"""
统计相差0.1的数量
"""

from itertools import product
import pandas as pd
import numpy as np
from SimiStock.config.path_config import *

if __name__ == '__main__':
    param_dict = {'method_name': ['叠加风格4'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [14],
                  # 'corr_threshold': [(8, 10), (7, 8), (6, 7), (5, 6)],
                  'corr_threshold': [(7, 10), (6, 10), (5, 10)],
                  'base_file': [(8, 10)],
                  #                  'corr_threshold': [(6, 8), (5, 8)],
                  #                  'base_file': [(7, 8)],
                  #                  'corr_threshold': [(5, 7)],
                  #                   'base_file': [(6, 7)],
                  'weight_kind': ['v0', 'v3']}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold'],
                              param_dict['weight_kind'],
                              param_dict['base_file']))
    ret_list = list()
    for param in param_list:
        print(param)
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        weight_kind = param[5]
        base_file = param[6]
        base_name = f'{method_name}_{hedge_max_num}_{base_file}_{weight_kind}_result.pkl'
        save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{weight_kind}_result.pkl'
        base_name_old = f'叠加风格3_{hedge_max_num}_{base_file}_{weight_kind}_result.pkl'
        save_name_old = f'叠加风格3_{hedge_max_num}_{corr_threshold}_{weight_kind}_result.pkl'
        hedge_list = pd.read_pickle(hedge_path + save_name)
        hedge_list_old = pd.read_pickle(hedge_path + save_name_old)
        for idx, _ in enumerate(hedge_list):
            hedges = hedge_list[idx]['hedge_list']
            old_hedges = hedge_list_old[idx]['hedge_list']
            ret_list.append([corr_threshold, base_file, len(old_hedges) - len(hedges)])
    check = pd.DataFrame(ret_list)
    check[3] = check[2] > 0
    total_check = check.groupby([0]).agg({3: sum})
    print(1)