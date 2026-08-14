import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_mimas_20240919_2(BaseFactor):
    strategy_name = "mimas"
    factor_name = "qyh_mimas_20240919_2"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "订单价格小于买10的部分，订单量/总挂买总量的离群程度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-总量强度" # 逻辑类别
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
            tick_df = filter_930(tick_df)
            database['Next1mTickfulladdorder'] = tick_df
            database['zcz'] = zcz
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['Next1mTickfulladdorder']
            zcz = database['zcz']
            tick_df = tick_df[tick_df['TotalBidQty'] > 0]
            if not zcz:
                tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.09).apply(lambda x: round_(x, 2))]
            else:
                tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.18).apply(lambda x: round_(x, 2))]
            tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (
                        tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'])
            res = (tick_df['factor'] ** 2).sum() / (tick_df['factor'].sum()) ** 2 if abs(
                tick_df['factor'].sum()) > 1e-3 else np.nan
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
