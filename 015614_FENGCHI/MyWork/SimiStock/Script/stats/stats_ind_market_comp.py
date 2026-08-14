# coding: utf-8
# Author：fengchi863
# Date ：2022/5/25 14:33

"""
测试申万行业以及全市场选股的结果差异
"""

from SimiStock.config.path_config import *
from SimiStock.SimiStockGenerator.util import util
import pandas as pd, numpy as np
from SimiStock.dataApi import getData
from tqdm import tqdm

if __name__ == '__main__':
    filename1 = '新版本_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_allMarket_20170101_20201231_result.pkl'
    filename2 = '新版本_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_SW1_20170101_20201231_result.pkl'

    all_list = pd.read_pickle(txTest_path + filename1)
    sw_list = pd.read_pickle(txTest_path + filename2)
    sw1 = getData.get_daily_1factor('SW1')

    print(len(all_list), len(sw_list))
    record_list = list()
    for hedge_list in tqdm(sw_list):
        stk_id = hedge_list['stk_id']
        trade_date = hedge_list['date']
        _hedge_stk_list = hedge_list['hedge_list'][0]['hedge_list']

        # 搜索全市场选出来的
        for hedge_list_allMarket in all_list:
            stk_id2 = hedge_list_allMarket['stk_id']
            trade_date2 = hedge_list_allMarket['date']
            if stk_id == stk_id2 and trade_date == trade_date2:
                _hedge_stk_list2 = hedge_list_allMarket['hedge_list'][0]['hedge_list']
                for N in range(1, 5):  # 前N个
                    common_pct = len(list(set(_hedge_stk_list[:N]).intersection(set(_hedge_stk_list2[:N])))) / N
                    ind_diff_num = 0
                    for stk in _hedge_stk_list2[:N]:
                        if sw1.loc[trade_date, stk] != sw1.loc[trade_date, stk_id]:
                            ind_diff_num += 1
                    ind_diff_num = ind_diff_num
                    ind_diff_pct = ind_diff_num / N
                    record_list.append([stk_id, trade_date, N, common_pct, ind_diff_num, ind_diff_pct])
    # print(len(record_list))
    util.save_list2pkl(record_list, other_stats_path, 'tmp_result.pkl')
    record_list = util.read_list(other_stats_path, 'tmp_result.pkl')
    record_df = pd.DataFrame(record_list, columns=['stk_id', 'trade_date', 'pre_num', 'common_pct',
                                                   'ind_diff_num', 'ind_diff_pct'])
    res = record_df.groupby(['pre_num'])[['common_pct', 'ind_diff_num', 'ind_diff_pct']].mean()
    output_dict = {
        '汇总': res,
        '全量': record_df,
    }
    util.save_dict2xls(output_dict, other_stats_path, '采用申万一级和全市场股票的差异.xlsx')
    util.send_file(other_stats_path, '采用申万一级和全市场股票的差异.xlsx')
    print(1)
