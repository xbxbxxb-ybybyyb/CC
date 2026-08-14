import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xly_neptune_t_1_b10(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xly_neptune_t_1_b10"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xly"  # 开发人员姓名
    factor_explain = "成交笔数占比" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_day_data = []
    xdb_data = [{'name': 'xdb_tick1m',  # xdb_order, xdb_trade, xdb_tick1s, xdb_tickfull, xdb_tickfulladdorder, xdb_tickex, xdb_cancel
                 'lag': 1  # 回看日期，N为往前回看1~N天
                 }]
    t_1_factor_data = []
    t_1_factor_data_types = []

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            tick_df = database['xdb_tick1m']
            dt, Ticker = tick_df.index[-1]
            try:
                tick_df = tick_df[tick_df['MDTime'] >= 93000000]
                tick_df = tick_df[tick_df['MDTime'] < 145700000]
                res = tick_df[tick_df['MDTime'] >= 143000000]['NumTrades'].sum()/tick_df['NumTrades'].sum()
                if np.isinf(res):
                    res = 1
            except:
                print('Exception: ', dt, Ticker)
                res = self.fill_na_value
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
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
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

