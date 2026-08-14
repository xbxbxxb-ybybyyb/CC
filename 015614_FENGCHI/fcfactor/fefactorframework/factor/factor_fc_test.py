# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 16:01

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_fc_test(BaseFactor):
    owner = 'fc'
    strategy_name = "saturn/sell"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "过去3日 相对于过去一年的差值"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = "是"

    t_day_data = []
    xdb_data = [
       #  {
       # 'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s, xdb_tickex
       # 'lag': 1}
    ]
    t_1_factor_data = [
        {'name': 'AShareMoneyFlow',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5',
         'lag': 10,  # 注意为正数
         'column': ['BUY_VALUE_EXLARGE_ORDER_ACT']}
    ]
    t_1_factor_data_types = ['AShareMoneyFlow']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        md_data = database['AShareMoneyFlow']  # 和上面t-1_factor_data的name一致
        res = md_data.rolling(10).mean().stack()
        database['pre_T_N'] = pd.DataFrame({self.factor_name: res})
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)