import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_mimas_20241226_3(BaseFactor):
    strategy_name = "mimas"
    factor_name = "qyh_mimas_20241226_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "小额订单中，订单价格大于9%部分，和市价差异的离散程度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['Next1mTickfulladdorder']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            tick_df = database['Next1mTickfulladdorder']
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            tick_df = filter_930(tick_df)
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'].diff().fillna(0)
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'].diff().fillna(0)
            database['Next1mTickfulladdorder'] = tick_df
            database['zcz'] = zcz
            database['bj'] = bj
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['Next1mTickfulladdorder']
            zcz = database['zcz']
            bj = database['bj']

            tick_df = tick_df[(tick_df['OrderQty'] * tick_df['OrderPrice']).apply(lambda x : round_(x,5)) < 50000]
            if zcz:
                tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.18).apply(lambda x: round_(x, 2))]
            elif bj:
                tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.27).apply(lambda x: round_(x, 2))]
            else:
                tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.09).apply(lambda x: round_(x, 2))]
            tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']

            res = tick_df['factor'].max() / tick_df['factor'].mean() if round_(tick_df['factor'].mean(),
                                                                               5) > 0 else np.nan

            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
