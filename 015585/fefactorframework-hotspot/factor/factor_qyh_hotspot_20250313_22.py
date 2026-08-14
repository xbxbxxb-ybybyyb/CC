import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_hotspot_20250313_22(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "qyh_hotspot_20250313_22"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            tick_df = database['TTickab']
            pre_close = tick_df['pre_close'].max()
            ff_shares = tick_df['ff_shares'].max()
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
            tick_df['MDTime_delta'] = tick_df['MDTime'].apply(
                    lambda x: get_time_delta(x) - 1800000) # 距离930毫秒数
            tick_df = filter_930(tick_df)
            database['TTickab'] = tick_df
            database['zcz'] = zcz
            database['bj'] = bj
            database['pre_close'] = pre_close
            database['ff_shares'] = ff_shares
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickab']
            zcz = database['zcz']
            bj = database['bj']
            #
            tick_df['factor'] = 0.5*(tick_df['HighPx'] + tick_df['LowPx']) / tick_df['pre_close']
            res = tick_df['factor'].mean()
            if zcz:
                res = (res-1)/2+1
            if bj:
                res = (res-1)/3+1
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)