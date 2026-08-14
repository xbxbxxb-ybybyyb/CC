import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xly_neptune_t_1_a52(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xly_neptune_t_1_a52"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xly"  # 开发人员姓名
    factor_explain = "涨跌幅因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 70,
         'column': ['high','low','amt','pct_chg','volume']}
    ]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']
            df_ori.loc[df_ori['pct_chg'] > 0.2, 'pct_chg'] = 0.2
            df_ori.loc[df_ori['pct_chg'] < -0.2, 'pct_chg'] = -0.2
            df_ori['factor'] = df_ori['pct_chg'] * 1e5/df_ori['amt']
            df_ori[self.factor_name] = df_ori['factor'].unstack().rolling(60,min_periods=1).mean().stack()
            df_ori[self.factor_name] = df_ori[self.factor_name].apply(lambda x: round_(x, 5))
            database['pre_T_N'] = df_ori[[self.factor_name]]
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            return res
