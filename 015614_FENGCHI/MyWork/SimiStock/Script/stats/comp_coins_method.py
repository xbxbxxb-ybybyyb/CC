# coding: utf-8
# Author：fengchi863
# Date ：2022/5/23 16:17

"""
对比不同的协整方案下的结果
"""

from SimiStock.config.path_config import *
import pandas as pd

hedge_name1 = '叠加协整性1_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result.pkl'
hedge_name2 = '叠加协整性2_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result.pkl'
hedge_name3 = '叠加协整性3_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result.pkl'

check_list1 = pd.read_pickle(hedge_name1)
check_list2 = pd.read_pickle(hedge_name2)
check_list3 = pd.read_pickle(hedge_name3)

"""
选出来的结果的排序差异：1和2
选出来的结果的数量差异：2和3
"""
for _hedge in check_list1:
    _stk_id = _hedge['stk_id']
    _date = _hedge['date']
    for tmp_hedge in check_list1:
        tmp_stk_id = tmp_hedge['stk_id']
        tmp_date = tmp_hedge['date']
        if tmp_stk_id == _stk_id and tmp_date == _date:
            stk_list = _hedge['hedge_list']['hedge_list']
            tmp_hedge_list = tmp_hedge['hedge_list']['hedge_list']
            s_corr = pd.Series(stk_list)

