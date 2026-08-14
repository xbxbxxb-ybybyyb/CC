import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_20241121_1(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_20241121_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买均价差、量价乘积的组合因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
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
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'].diff().fillna(0)
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'].diff().fillna(0)
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
            tick_df['factor2'] = (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx']) / (tick_df['pre_close'])
            tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
            tick_df2 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
            tick_df1['factor1'] = (tick_df1['LastPx'] / tick_df1['pre_close'] - 1) * tick_df1['VolumeTrade']
            tick_df3 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.75),5)]
            tick_df4 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),5)]
            res4 = tick_df4['factor2'].tail(1).mean() - tick_df3['factor2'].tail(1).mean()
            res3 = tick_df['ValueTrade'].sum()/ tick_df['VolumeTrade'].sum() / tick_df['pre_close'].tail(1).values[0] - 1 \
                if round_(tick_df['VolumeTrade'].sum(),5) > 10 else np.nan
            if zcz:
                tick_df1['factor1'] = tick_df1['factor1'] / 2
                tick_df2['factor2'] = tick_df2['factor2'] / 2
                res3 = res3/2
                res4 = res4/2
            if bj:
                tick_df1['factor1'] = tick_df1['factor1'] / 3
                tick_df2['factor2'] = tick_df2['factor2'] / 3
                res3 = res3/3
                res4 = res4/3
            res1 = tick_df1['factor1'].median()
            res2 = tick_df2['factor2'].median()
            # 历史值标准化
            res2 = (res2 - 0.041)/0.031
            res3 = (res3 - 0.042)/0.023
            res1 = (res1 - 2453)
            res4 = (res4 + 0.011) / 0.019
            res1 = 0 if np.isnan(res1) else res1
            res2 = 0 if np.isnan(res2) else res2
            res3 = 0 if np.isnan(res3) else res3
            res4 = 0 if np.isnan(res4) else res4
            res = min(round_(res3 + res2,6), round_(res4,6)) * res1
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
