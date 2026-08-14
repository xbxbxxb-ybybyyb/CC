# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
"""
'MDTime',
'OrderIndex',
'OrderBSFlag',
'OrderPrice',
'OrderQty',
'appl_seq_num',
'pre_close',
'ff_shares'
"""

class factor_fc_n20250320_1(BaseFactor):
    owner = 'fc'
    strategy_name = "europa"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = False
    factor_explain = "不同价格区间，买卖撤单量差异的比值"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = "是"

    t_day_data = ['TCancelprice']
    xdb_data = [
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
            df = database['TCancelprice']

            if len(df) > 0:
                df['OrderMoney'] = df['OrderQty'] * df['OrderPrice']
                seg_threshold = df['OrderPrice'].quantile(0.75)
                part_df1 = df.query(f'OrderPrice >= {seg_threshold}')
                part_df2 = df.query(f'OrderPrice <= {seg_threshold}')
            else:
                factor_dict = {self.factor_name: 0}
                return pd.Series(factor_dict)

            res11 = part_df1.query('OrderBSFlag == 1')['OrderQty'].sum()
            res12 = part_df1.query('OrderBSFlag == 2')['OrderQty'].sum()
            res1 = res11 / res12 if res12 != 0 else 1e5

            res21 = part_df2.query('OrderBSFlag == 1')['OrderQty'].sum()
            res22 = part_df2.query('OrderBSFlag == 2')['OrderQty'].sum()
            res2 = res21 / res22 if res22 !=0 else 1e5

            factor_dict = {self.factor_name: res1 / res2 if res2 != 0 else 1e5}
            return pd.Series(factor_dict)
