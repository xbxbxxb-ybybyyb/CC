import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptune_shortterm_20250626_19(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_shortterm_20250626_19"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "ttickab1m 买均价差 统计量" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "短周期-价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['T1mTickab']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            tick_df = database['T1mTickab']
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
            tick_df = filter_930(tick_df)
            database['T1mTickab'] = tick_df
            database['zcz'] = zcz
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['T1mTickab']
            zcz = database['zcz']
            #
            tick_df['factor'] = (tick_df['ValueTrade']/(tick_df['VolumeTrade']+1e-5) - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])
            if zcz:
                tick_df['factor'] = tick_df['factor']/2
            tick_df = tick_df[tick_df['ValueTrade'] > 1e-5]
            res =  tick_df['factor'].max() / tick_df['factor'].mean() if tick_df['factor'].mean() > 1e-5 else np.nan
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
