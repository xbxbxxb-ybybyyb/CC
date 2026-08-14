# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
# 逻辑：T-3到T-1日基于全息盘口的每日lastpx中位数的均值
class factor_qyh_new_fulltick_1(BaseFactor):

    strategy_name = "jupiter/europa"
    factor_name = "qyh_new_fulltick_1"
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tickfull', # xdb_order, xdb_trade, xdb_cancel, xdb_tickfull, xdb_tick1s
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]

    fill_na_value = 1
    need_pre_calculate_T_N = True

    def pre_calculate_T_N_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        # 例：若当前因子计算产生两个中间变量test1, test2，则跳过计算是返回值应写成如下形式
        # 可以返回Series，和普通T日因子返回格式类似；也可以返回df（纯h5因子）
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tickfull_df = database['xdb_tickfull']
        tickfull_df = tickfull_df[tickfull_df['LastPx'] > 0]
        res = tickfull_df.groupby('MDDate')['LastPx'].median().mean()
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

