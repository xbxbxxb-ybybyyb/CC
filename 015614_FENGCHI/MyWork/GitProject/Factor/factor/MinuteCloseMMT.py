# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class MinuteCloseMMT(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_adj_minute","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.high_badj",
    "FactorData.Basic_factor.volume_adj_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.low_badj",
    "FactorData.Basic_factor.amt"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 5
    lag = 5
    fix_times=["1500"]
    def calc_single(self,database):
        data_min = {"FactorData.Basic_factor.close_adj_minute":database.depend_data['FactorData.Basic_factor.close_adj_minute'],
                   "FactorData.Basic_factor.volume_adj_minute":database.depend_data['FactorData.Basic_factor.volume_adj_minute'],
                  'FactorData.Basic_factor.amt_minute':database.depend_data['FactorData.Basic_factor.amt_minute'] }
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        MinuteClose = data_min['FactorData.Basic_factor.close_adj_minute']
        MinuteVolume = data_min['FactorData.Basic_factor.volume_adj_minute']
        MinuteTurnover = data_min['FactorData.Basic_factor.amt_minute']
        close_adj =database.depend_data['FactorData.Basic_factor.close_badj']
        high_adj = database.depend_data['FactorData.Basic_factor.high_badj']
        low_adj = database.depend_data['FactorData.Basic_factor.low_badj']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        
        
        up_var = self.minute_help(MinuteTurnover,MinuteClose,MinuteVolume)
        
        n = 5
        close_chg = close_adj / close_adj.rolling(window=n).mean()
        amt_chg = amt / amt.rolling(window=n).mean()
        amp = high_adj - low_adj
        amp_chg = amp/amp.rolling(window=n).mean()        
        close_chg_scale = close_chg.rank(pct=True,axis=1)
        amt_chg_scale = amt_chg.rank(pct=True,axis=1)
        amp_chg_scale = amp_chg.rank(pct=True,axis=1)
        daily_adj = (1-close_chg_scale.shift(1).iloc[-1,:])*(1+amt_chg_scale.shift(1).iloc[-1,:])*(1+amp_chg_scale.shift(1).iloc[-1,:])
#         daily_adj.fillna(method='bfill',inplace=True)
        
        factor = daily_adj*up_var.iloc[-1,:]
        return factor
    
    def minute_help(self,MinuteTurnover,MinuteClose,MinuteVolume): 
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        df_skew = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteTurnover.columns)
        tail_len = 30
        for date in date_list:
            Turnover = MinuteTurnover.loc[date]
            Close = MinuteClose.loc[date]
            Volume = MinuteVolume.loc[date]

            vwap = Turnover/Volume           

            Close_chg = Close.iloc[-1]/Close[:tail_len].mean()
            Close_std = Close[-30:].std()
            Close_adj = Close_chg/Close_std
            Close_adj_rank = Close_adj.rank(pct=True)

            Turnover_part = Turnover[-2:].sum()
            Turnover_ref = Turnover[-30:-2].mean() # 基准剔除集合竞价
            Turnover_part_chg = (Turnover_part - Turnover_ref)/Turnover_ref
            Turnover_part_chg_rank = Turnover_part_chg.rank(pct=True)            

            # 计算price_up_rate
            factor = (1+Close_adj_rank)*(1-Turnover_part_chg_rank)

            df_skew.loc[date]=factor       
        return df_skew


