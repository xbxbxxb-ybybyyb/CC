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


class factor_fc_n20250320_2(BaseFactor):
    owner = 'fc'
    strategy_name = "mimas"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = False
    factor_explain = "高价区间内总撤单金额"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = "是"

    t_day_data = ['Next1mCancel']
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
            df = database['Next1mCancel']

            if len(df) > 0:
                df['OrderMoney'] = df['OrderQty'] * df['OrderPrice']
                seg_threshold = df['OrderPrice'].quantile(0.75)
                part_df1 = df.query(f'OrderPrice >= {seg_threshold}')
            else:
                factor_dict = {self.factor_name: 0}
                return pd.Series(factor_dict)

            res = part_df1['OrderMoney'].sum()

            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)
