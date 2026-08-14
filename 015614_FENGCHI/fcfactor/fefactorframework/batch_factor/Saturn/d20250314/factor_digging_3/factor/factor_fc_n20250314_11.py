# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
"""
'MDDate',
'MDTime',
'appl_seq_num',
'OrderIndex',
'OrderPrice',
'OrderQty',
'OrderBSFlag',
'ff_shares',
'pattern',
'industry',
'after_not_ul_len',
'pre_close',
'ul_price',
'dl_price'
"""

param1, param2, param3 = "OrderMoney", 0.75, "OrderMoney" # 配置超参数

class factor_fc_n20250314_11(BaseFactor):
    owner = 'fc'
    strategy_name = "saturn"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = False
    factor_explain = "过去3日 相对于过去一年的差值"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = "是"

    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_cancel', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s, xdb_tickex
       'lag': 1}
    ]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df = database['xdb_cancel']
            df['OrderMoney'] = df['OrderQty'] * df['OrderPrice']
            seg_threshold = df[param1].quantile(param2)
            if len(df) > 0:
                part_df1 = df.query(f'{param1} >= {seg_threshold}')
            else:
                factor_dict = {self.factor_name: 0}
                return pd.Series(factor_dict)

            res11 = part_df1.query('OrderBSFlag == 1')[param3].sum()
            res12 = part_df1.query('OrderBSFlag == 2')[param3].sum()
            res1 = res11 / res12 if res12 != 0 else 1e5

            factor_dict = {self.factor_name: res1}
            return pd.Series(factor_dict)
