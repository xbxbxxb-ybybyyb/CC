# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

param1, param2, param3 = "BUY_VOLUME_EXLARGE_ORDER_ACT", 1, 120 # 配置超参数

class factor_fc_T1_20240321_967(BaseFactor):
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
         'lag': 250,  # 注意为正数
         'column': [param1]}
    ]
    t_1_factor_data_types = ['AShareMoneyFlow']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        md_data = database['AShareMoneyFlow']  # 和上面t-1_factor_data的name一致
        b = md_data[param1].unstack().rolling(param2, min_periods=1).median().stack()
        a = md_data[param1].unstack().rolling(param3, min_periods=1).median().stack()
        database['pre_T_N'] = pd.DataFrame({self.factor_name: b-a})
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df
