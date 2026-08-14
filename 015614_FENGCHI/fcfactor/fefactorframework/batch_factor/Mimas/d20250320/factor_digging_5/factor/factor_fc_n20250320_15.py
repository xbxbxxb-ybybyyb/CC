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

param1, param2, param3 = "OrderQty", 0.5, "OrderMoney" # 配置超参数

class factor_fc_n20250320_15(BaseFactor):
    owner = 'fc'
    strategy_name = "mimas"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = False
    factor_explain = "过去3日 相对于过去一年的差值"
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
                seg_threshold = df[param1].quantile(param2)
                part_df1 = df.query(f'{param1} >= {seg_threshold}')
                part_df2 = df.query(f'{param1} <= {seg_threshold}')
            else:
                factor_dict = {self.factor_name: 0}
                return pd.Series(factor_dict)

            res1 = part_df1[param3].count()
            res2 = part_df2[param3].count()
            res = res1 / res2 if res2 != 0 else 1e5

            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)
