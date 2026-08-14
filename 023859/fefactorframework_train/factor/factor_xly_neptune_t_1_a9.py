import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xly_neptune_t_1_a9(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xly_neptune_t_1_a9"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xly"  # 开发人员姓名
    factor_explain = "价格std" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 10,
         'column': ['high','close']}
    ]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致
            df_ori['factor'] = (df_ori['high']-df_ori['close'])/(df_ori['high']+df_ori['close'])
            df_ori[self.factor_name] = df_ori['factor'].unstack().rolling(3,min_periods=1).std().stack()
            df_ori[self.factor_name] = df_ori[self.factor_name].apply(lambda x: round_(x, 5))  # 矩阵大小不同时，Python精度差异，导致计算值不同
            database['pre_T_N'] = df_ori[[self.factor_name]]
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            return res
