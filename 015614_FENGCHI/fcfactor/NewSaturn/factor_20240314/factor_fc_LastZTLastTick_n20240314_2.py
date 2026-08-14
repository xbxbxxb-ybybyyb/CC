# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_fc_LastZTLastTick_n20240314_2(BaseFactor):
    owner = 'fc'
    strategy_name = "saturn/sell"
    factor_name = "fc_LastZTLastTick_n20240314_2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "上午委托单比值CV + 买卖压力比值CV"
    zcz_adjusted = "否"
    logic_type = "筹码分布"
    low_cost = "是"
    # 44.625, -0.09279953901937586

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
        zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
        df = df.query(f'LastPx != 0')
        df = df.query('93000000 <= MDTime <= 113000000')

        df['tick_volume'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift().fillna(0)

        order_ratio = df['tick_volume'] / (df[['Buy%dOrderQty' % (j + 1) for j in range(3)]].sum(axis=1) + df[['Sell%dOrderQty' % (j + 1) for j in range(3)]].sum(axis=1))
        b2s_ratio = (df[['Buy%dOrderQty' % (j + 1) for j in range(3)]].sum(axis=1) / df[['Sell%dOrderQty' % (j + 1) for j in range(3)]].sum(axis=1))
        order_ratio[np.abs(order_ratio) == np.inf] = 0
        b2s_ratio[np.abs(b2s_ratio) == np.inf] = 0

        if order_ratio.std() != 0:
            res1 = order_ratio.std() / order_ratio.mean()
        else:
            res1 = 0

        if b2s_ratio.std() != 0:
            res2 = b2s_ratio.std() / b2s_ratio.mean()
        else:
            res2 = 0
        res = res1 + res2
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
