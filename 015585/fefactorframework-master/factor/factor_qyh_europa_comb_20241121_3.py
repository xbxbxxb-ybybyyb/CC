import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_comb_20241121_3(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_comb_20241121_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "相对上影线、买均价差等的组合" # 因子逻辑解释
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
            tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
            tick_df2 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
            tick_df3 = tick_df.head(20) if len(tick_df) > 20 else tick_df
            tick_df4 = tick_df.tail(20) if len(tick_df) > 20 else tick_df
            #
            tick_df1['pcummax'] = tick_df1['LastPx'].cummax()
            tick_df1['pcummin'] = tick_df1['LastPx'].cummin()
            tick_df1['amp'] = tick_df1['pcummax'] - tick_df1['pcummin']
            tick_df1['amp'] = tick_df1['amp'].apply(lambda x: np.nan if abs(x) < 0.0001 else x)
            tick_df1['syx1'] = (tick_df1['pcummax'] - tick_df1['LastPx']) \
                              / tick_df1['amp']
            tick_df2['factor'] = (tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx'])/(tick_df2['pre_close'])
            tick_df4['factor'] = (tick_df4['ValueTrade']/(tick_df4['VolumeTrade']) - tick_df4['WeightedAvgBidPx'])/(tick_df4['pre_close'])
            #
            res1 = tick_df1['syx1'].max() / tick_df1['syx1'].mean() if round_(tick_df1['syx1'].mean(),5)>0 else 0
            res2 = tick_df2['factor'].std() / tick_df2['factor'].mean() if round_(abs(tick_df2['factor'].mean()),8) > 1e-4 else 0
            res3 = ((tick_df3['LastPx'] - tick_df3['LastPx'].shift(1))/tick_df3['pre_close']).max() \
                   - ((tick_df4['LastPx'] - tick_df4['LastPx'].shift(1))/tick_df4['pre_close']).max()
            res4 = tick_df4['factor'].std() / tick_df4['factor'].mean()
            if np.isnan(res4):
                res4 = 0
            elif not round_(abs(tick_df4['factor'].mean()),8) > 1e-8:
                res4 = 0
            #
            if zcz:
                res3 = res3/2
            if bj:
                res3 = res3/3
            if round_(abs(res3 - res4),5) > 1e-3:
                if round_(abs(res2),5) > 1e-3:
                    res = res1 / res2 / (res3 - res4)
                else:
                    res = res1 / (res3 - res4)
            else:
                res = res1
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
