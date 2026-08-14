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

param1, param2, param3 = "OrderMoney", 0.75, "OrderQty" # 配置超参数

class factor_fc_n20250320_12(BaseFactor):
    owner = 'fc'
    strategy_name = "metis"
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
       'lag': 1},
        {'name': 'xdb_trade', 'lag': 1}
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
            trade_df = database['xdb_trade']
            ul_price = trade_df['TradePrice'].max()
            zt_time = trade_df[trade_df['TradePrice'] == ul_price]['MDTime'].min()

            df = database['xdb_cancel']
            df = df.query(f'MDTime <= {zt_time}')

            df['OrderMoney'] = df['OrderQty'] * df['OrderPrice']
            seg_threshold = df[param1].quantile(param2)
            if len(df) > 0:
                part_df1 = df.query(f'{param1} >= {seg_threshold}')
                part_df2 = df.query(f'{param1} <= {seg_threshold}')
            else:
                factor_dict = {self.factor_name: 0}
                return pd.Series(factor_dict)

            res11 = part_df1.query('OrderBSFlag == 1')[param3].count()
            res12 = part_df1.query('OrderBSFlag == 2')[param3].count()
            res1 = res11 / res12 if res12 != 0 else 1e5

            res21 = part_df2.query('OrderBSFlag == 1')[param3].count()
            res22 = part_df2.query('OrderBSFlag == 2')[param3].count()
            res2 = res21 / res22 if res22 != 0 else 1e5

            factor_dict = {self.factor_name: res1 / res2 if res2 != 0 else 1e5}
            return pd.Series(factor_dict)
