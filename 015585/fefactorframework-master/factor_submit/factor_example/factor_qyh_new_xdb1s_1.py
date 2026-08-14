# xdb
import os

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_new_xdb1s_1(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_new_xdb1s_1"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T-2到T-1日基于xdb_tick1s的每日lastpx中位数的均值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tick1s', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 2 # 回看日期，N为往前回看1~N天
    }]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            # database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tickfull_df = database['xdb_tick1s']
        tickfull_df = tickfull_df[tickfull_df['LastPx'] > 0]
        res = tickfull_df.groupby('MDDate')['LastPx'].median().mean() # 得到1s计算的均价
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            return database
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

