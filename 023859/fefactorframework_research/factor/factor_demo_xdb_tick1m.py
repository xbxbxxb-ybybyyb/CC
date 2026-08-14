import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_demo_xdb_tick1m(BaseFactor):
    strategy_name = "neptune"
    factor_name = "demo_xdb_tick1m"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m', # xdb_order1m, xdb_tick1m
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        res = data['LastPx'].std()
        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res