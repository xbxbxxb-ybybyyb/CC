import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_20240725_1(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_20240725_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "挂买未成交订单中，小额订单价格和市场价差异的集中度" # 因子逻辑解释
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
            tick_df = filter_930(tick_df)
            database['TTickfulladdorder'] = tick_df
            database['zcz'] = zcz
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickfulladdorder']
            zcz = database['zcz']
            tick_df = tick_df[tick_df['OrderType'] == 'b1']
            tick_df = tick_df[(tick_df['OrderQty'] * tick_df['OrderPrice']).apply(lambda x : round_(x,5)) < 50000]
            tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x: get_time_delta(x))
            tick_df = tick_df[tick_df['MDTime_delta'] >= (tick_df['MDTime_delta'].max() - 60 * 1000)]
            tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']
            res = (tick_df['factor'] ** 2).sum() / (tick_df['factor'].sum()) ** 2 if abs(
                tick_df['factor'].sum()) > 1e-3 else np.nan
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
