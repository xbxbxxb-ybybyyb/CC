# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_newmetis_20240201_1(BaseFactor):
    strategy_name = "metis"
    factor_name = "qyh_newmetis_20240201_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False # 纯T日数据不需要pre_T_N
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买均和成交价差对应涨跌幅的mean - min" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ["TTickab_MetisAll"]
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
        else:
            tick_df = database['TTickab_MetisAll']
            tick_df = filter_930(tick_df) # 这里使用公共函数
            database['TTickab_MetisAll'] = tick_df
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            EPS = 1e-9
            tick_df = database['TTickab_MetisAll']
            if tick_df.shape[0] > 0:
                xx = tick_df['pre_close']
                yy = tick_df['WeightedAvgBidPx'] - tick_df['LastPx']
                res = xx / (EPS + yy)
                result = res.mean() - res.min()
            else:
                result = 0.0
            factor_dict = {self.factor_name: result / 1e4}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
