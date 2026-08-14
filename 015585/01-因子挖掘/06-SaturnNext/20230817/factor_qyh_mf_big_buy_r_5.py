#
# 大单买入金额占比,5日平均
# gg
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_mf_big_buy_r_5'
def factor_qyh_mf_big_buy_r_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.11,'data':['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -90)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['BUY_VALUE_EXLARGE_ORDER',
                                   'BUY_VALUE_LARGE_ORDER',
                                   'BUY_VALUE_MED_ORDER',
                                   'BUY_VALUE_SMALL_ORDER']
                          , alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')
    f_data[factor_name] = f_data['BUY_VALUE_LARGE_ORDER'] / \
                          (f_data['BUY_VALUE_EXLARGE_ORDER'] +
                           f_data['BUY_VALUE_LARGE_ORDER'] +
                           f_data['BUY_VALUE_MED_ORDER'] +
                           f_data['BUY_VALUE_SMALL_ORDER'])
    f_data[factor_name] = f_data[factor_name].unstack().rolling(5,1).mean().stack()
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。