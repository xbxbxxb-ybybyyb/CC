import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_20241205_11(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_20241205_11"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "撤卖订单中，高于卖10时，最后100单订单价格与市价差异对应涨跌幅的集中度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickfulladdorder']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            tick_df = database['TTickfulladdorder']
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            tick_df = filter_930(tick_df)
            database['TTickab'] = tick_df
            database['zcz'] = zcz
            database['bj'] = bj
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickab']
            zcz = database['zcz']
            bj = database['bj']
            #
            tick_df = tick_df[tick_df['OrderType'] == 'co']
            tick_df = tick_df[tick_df['Sell10Price'] > 0]
            tick_df = tick_df[tick_df['OrderPrice'] >= tick_df['Sell10Price']]
            tick_df = tick_df.tail(100) if len(tick_df) > 100 else tick_df
            tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']
            res = (tick_df['factor'] ** 2).sum() / (tick_df['factor'].sum()) ** 2 if abs(
                tick_df['factor'].sum()) > 1e-3 else np.nan
            # if zcz:
            #     res = res/2
            # if bj:
            #     res = res/3
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
