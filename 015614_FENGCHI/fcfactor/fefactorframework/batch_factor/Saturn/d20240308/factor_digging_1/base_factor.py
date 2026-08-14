# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

param1, param2 = 3, 5   # 配置超参数

class factor_fc_LastZTLastTick_n20240307_1(BaseFactor):
    owner = 'fc'
    strategy_name = "saturn/sell"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "T-1日ZT后第一个tick成交额占全天最大成交额的比例"
    zcz_adjusted = "否"
    logic_type = "筹码分布"
    low_cost = "是"

    # 41.083333333333336, -0.07092930459726264
    t_day_data = []
    xdb_data = [{
       'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s, xdb_tickex
       'lag': 1
    }]
    t_1_factor_data = []
    t_1_factor_data_types = []

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        df = database['xdb_tickex']
        dt, Ticker = df.index[0]
        pre_close = df.iloc[-1]['pre_close']
        ff_shares = df.iloc[-1]['ff_shares']
        df = df.query('MDTime >= 93000000')
        zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
        zt_price = df['LastPx'].max()
        zt_time = df[df['LastPx'] == zt_price]['MDTime'].min()
        df = df.query(f'LastPx != 0')
        df1 = df.query('MDTime >= 93000000')
        zt_time_end = fun_get_time(zt_time, 1200)
        df2 = df.query(f'{zt_time} <= MDTime <= {zt_time_end}')

        if len(df) >= 1:
            after_zt_amt = (df2['TotalBidQty'] * df2['WeightedAvgBidPx']).head(1).sum()
        else:
            after_zt_amt = (df2['TotalBidQty'] * df2['WeightedAvgBidPx']).sum()

        value_max = df1['TotalValueTrade'].max()
        if value_max != 0:
            res = after_zt_amt / value_max
        else:
            res = 0
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
