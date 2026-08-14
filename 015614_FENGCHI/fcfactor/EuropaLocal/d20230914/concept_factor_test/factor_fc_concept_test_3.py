# coding: utf-8
# Author：fengchi863
# Date ：2023/9/12 8:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
import numpy as np

def trans_int2windcode(code):
    if isinstance(code, str):
        return code
    elif isinstance(code, (float, int, np.int, np.int64)):
        temp = str(int(code)).zfill(6)
        if temp[0] == '9' and len(temp) == 7:  # 指数
            if temp[1] == '3':
                result = temp[1:] + '.SZ'
            else:
                result = temp[1:] + '.SH'
        elif temp[0] == '0' or temp[0] == '3':
            result = temp + '.SZ'
        elif temp[0] == '6':
            result = temp + '.SH'
        else:
            result = temp + 'SH'
        return result
    else:
        raise Exception('input code type error')

def factor_fc_concept_test_3(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -10)[0])
    concept_data = pd.read_pickle('/data/user/015614/junkData/concept_factor.pkl')

    concept_data['dt'] = concept_data.index.get_level_values(0).map(lambda x: pd.to_datetime(str(x)))
    concept_data['Ticker'] = concept_data.index.get_level_values(1).map(lambda x: trans_int2windcode(x))
    concept_data = concept_data.set_index(['dt', 'Ticker'])
    factor_df = pd.DataFrame()
    factor_df[factor_name] = concept_data['昨日所属Wind概念最大涨跌幅']
    """
     '所属Wind概念数量',
     '所属SW2概念数量',
     '昨日所属Wind概念最大涨跌幅',
     '昨日所属Wind概念平均涨跌幅',
     '昨日所属SW2涨跌幅',
     '昨日所属Wind概念涨停个数',
     '昨日所属Wind概念触板个数',
     '昨日所属SW2涨停个数',
     '昨日所属SW2触板个数'
    """
    return factor_df