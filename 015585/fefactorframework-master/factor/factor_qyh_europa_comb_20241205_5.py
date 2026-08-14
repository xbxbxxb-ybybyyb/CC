import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_europa_comb_20241205_5(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_europa_comb_20241205_5"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "成交笔数、买卖均价的统计量组合因子" # 因子逻辑解释
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
            #
            tick_df2 = tick_df.head(20) if len(tick_df) > 20 else tick_df
            tick_df3 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
            #
            tick_df['factor1'] = tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)
            tick_df2['factor2'] = (tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx'])/(tick_df2['pre_close'])
            tick_df3['factor3'] = (tick_df3['Sell1Price'] - tick_df3['WeightedAvgOfferPx'])/(tick_df3['pre_close'])
            #
            res1 = (tick_df['factor1']**2).sum() / (tick_df['factor1'].sum())**2 if abs(tick_df['factor1'].sum()) > 1e-3 else 0
            res2 = tick_df2['factor2'].median()
            res3 = tick_df3['factor3'].min()
            #
            if zcz:
                res2 = res2 / 2
                res3 = res3 / 2
            if bj:
                res2 = res2 / 3
                res3 = res3 / 3
            #
            res = abs(res1 - res2 - res3)
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
