import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_20250403_45(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250403_45"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "笔均成交额波动" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = ['T1mTickab']
    #
    # xdb_data = [
    #     {
    #    'name': 'xdb_trade', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
    #    'lag': 1 # 回看日期，N为往前回看1~N天
    # }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            tick_df = database['T1mTickab']
            tick_df = filter_930(tick_df)  # 公共函数
            database['T1mTickab'] = tick_df
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            data = database['T1mTickab']
            data['ValueTrade'] = data['TotalValueTrade'] - data['TotalValueTrade'].shift(1).fillna(0)
            data['NumTrade'] = data['NumTrades'] - data['NumTrades'].shift(1).fillna(0)
            res = (data['ValueTrade'] / data['NumTrade']).std()

            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
