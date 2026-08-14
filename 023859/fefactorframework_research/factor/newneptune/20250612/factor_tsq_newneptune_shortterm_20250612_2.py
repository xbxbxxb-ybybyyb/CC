import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_shortterm_20250612_2(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_shortterm_20250612_2"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "高价成交量占比" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "短周期-买单强度-总量强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['T1mTransaction']
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        return database

    def prepare_T_data(self, database):
        trans_df = database['T1mTransaction']
        database['T1mTransaction'] = trans_df

        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            data = database['T1mTransaction']
            data = data[(data['TradePrice'] > 0)]
            if len(data):
                close = data['TradePrice'].iloc[-1]
                res = data[(data['TradeBSFlag'] == 1) & (data['TradePrice'] >= close)]['TradeQty'].sum() / data['TradeQty'].sum()
            else:
                res = np.nan

        factor_dict = {self.factor_name: res}
        return pd.Series(factor_dict)
