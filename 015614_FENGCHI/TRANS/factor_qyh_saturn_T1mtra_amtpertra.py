# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
# 逻辑：T日09:31数据，单笔成交额
class factor_qyh_saturn_T1mtra_amtpertra(BaseFactor):

    strategy_name = "saturn/sell"
    factor_name = "qyh_saturn_T1mtra_amtpertra"
    t_day_data = ["T1mTransaction"]
    fill_na_value = 24125
    need_pre_calculate_T_N = False

    def pre_calculate_T_N_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        # 例：若当前因子计算产生两个中间变量test1, test2，则跳过计算是返回值应写成如下形式
        if database["skip"] == True:
            return database
        return database

    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            transaction_df = database['T1mTransaction']
            transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]
            database['T1mTransaction'] = transaction_df
        return database

    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            transaction_df = database['T1mTransaction']
            if transaction_df.empty:
                amtpertra = 0
            else:
                amtpertra = transaction_df['TradeMoney'].sum() / transaction_df['TradeMoney'].count()
            factor_dict = {self.factor_name: amtpertra}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
