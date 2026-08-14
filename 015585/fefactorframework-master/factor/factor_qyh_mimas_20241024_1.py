import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_mimas_20241024_1(BaseFactor):
    strategy_name = "mimas"
    factor_name = "qyh_mimas_20241024_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "大额订单中，订单价格>市价*1.01的部分，订单总量占挂卖总量的中位数" # 因子逻辑解释
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
            # zcz = database['zcz']
            tick_df = tick_df[(tick_df['OrderQty'] * tick_df['OrderPrice']).apply(lambda x : round_(x,2)) >= 200000]
            tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['LastPx'] * 1.01).apply(lambda x: round_(x, 5))]
            tick_df = tick_df[tick_df['TotalOfferQty'] > 0]
            tick_df['factor'] = (tick_df['OrderQty'] / tick_df['TotalOfferQty'])
            res = tick_df['factor'].median()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
