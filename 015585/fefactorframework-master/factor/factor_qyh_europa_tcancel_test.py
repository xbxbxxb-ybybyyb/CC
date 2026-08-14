import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_tcancel_test(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_tcancel_test"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = " " # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TCancelprice']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
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
            tick_df = database['TCancelprice']
            res = tick_df['OrderQty'].mean()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
