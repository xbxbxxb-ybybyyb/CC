# coding: utf-8
# Author：fengchi863
# Date ：2022/3/22 14:42

import pandas as pd

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from itertools import product


if __name__ == '__main__':
    # filename = '叠加风格3_14_(8, 10)_v0_result.pkl'
    # filename = '叠加风格3_14_(7, 10)_v0_result.pkl'
    filename = '叠加风格5_14_0.8_v3_95_20180101_20200630_result.pkl'
    hedge_list = pd.read_pickle(hedge_path + filename)
    stats_result = util.stats_hedge_list(hedge_list)

    # check = pd.read_pickle(hedge_path + '叠加风格3_14_(8, 10)_v3_result.pkl_include_stk.pkl')
    # print(len(check))

    # param_dict = {'method_name': ['叠加风格3'],
    #               'concept': ['SW1'],
    #               'pre_days_num': [120],
    #               'hedge_max_num': [14],
    #               'corr_threshold': [(8, 10), (7, 10), (6, 10), (5, 10),
    #                                  (7, 8), (6, 8), (5, 8),
    #                                  (6, 7), (5, 7),
    #                                  (5, 6)],
    #               'weight_kind': ['v0', 'v3']}
    # param_list = list(product(param_dict['method_name'],
    #                           param_dict['concept'],
    #                           param_dict['pre_days_num'],
    #                           param_dict['hedge_max_num'],
    #                           param_dict['corr_threshold'],
    #                           param_dict['weight_kind']))
    # ret_dict = dict()
    # for param in param_list:
    #     method_name = param[0]
    #     concept = param[1]
    #     pre_days_num = param[2]
    #     hedge_max_num = param[3]
    #     corr_threshold = param[4]
    #     weight_kind = param[5]
    #     save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{weight_kind}_result.pkl'
    #     hedge_list = pd.read_pickle(hedge_path + save_name)
    #     stats_result = util.stats_hedge_list(hedge_list, output_name=f'stats_{save_name}.xlsx')
    #     output_name = f'stats_{save_name}.xlsx'
    #     check = pd.read_excel(other_stats_path + output_name, sheet_name='汇总', index_col=0)
    #     num = check.loc['大于1的项目数量', 0]
    #     ret_dict[corr_threshold] = num
    # ret = pd.Series(ret_dict)
    # print(1)