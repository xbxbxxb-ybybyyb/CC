# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_mkind_1(BaseFactor):
    strategy_name = "europa"
    factor_name = "qyh_mkind_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False # 纯T日数据不需要pre_T_N
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买均和成交价差对应涨跌幅的mean - min" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ["MarketTTick_All"]
    xdb_data = []
    t_1_factor_data = []
    t_1_factor_data_types = []

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 这两行不涉及T_N数据，运行中是无效的，但建议保留，防止复制粘贴导致忘记处理
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
            result = 100
            factor_dict = {self.factor_name: result}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
