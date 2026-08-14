from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class HF_ReverseVolRatioVWAP(BaseFactor):
    """
    *因子名 : HF_ReverseVolRatioVWAP
    *因子功能描述 : 5日均价线下方反弹和上方回调分钟线的成交量占比

    *因子参数 : vwap -- 日均价 amt -- 日成交额 open_minute -- 分钟开盘价, amt_minute -- 分钟成交额
    *作者 : 卢泽宁
    *因子创建日期 : 2020.02.09
    """
    factor_type = "FIX"
    s_amt = 'FactorData.Basic_factor.amt'
    s_vol = 'FactorData.Basic_factor.volume'
    s_adj = 'FactorData.Basic_factor.adjfactor'
    s_open_adj_min = 'FactorData.Basic_factor.open_adj_minute'
    s_close_adj_min = 'FactorData.Basic_factor.close_adj_minute'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    depend_data = [s_amt, s_vol, s_adj, s_open_adj_min, s_close_adj_min, s_amt_min]
    lag = 5
    minute_lag = 0
    # reform_window = 5

    def calc_single(self, database):
        data_min = {self.s_open_adj_min : database.depend_data[self.s_open_adj_min],
                    self.s_close_adj_min : database.depend_data[self.s_close_adj_min],
                    self.s_amt_min : database.depend_data[self.s_amt_min]
        }
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        open_adj_min = data_min[self.s_open_adj_min]
        close_adj_min = data_min[self.s_close_adj_min]
        amt_min = data_min[self.s_amt_min]
        amt = database.depend_data[self.s_amt]
        vol = database.depend_data[self.s_vol]
        adj = database.depend_data[self.s_adj]
        # 计算五日vwap_adj
        vol_adj = vol / adj
        vwap_adj =  (amt * vol_adj).sum() / vol_adj.sum()
        # 计算今日五日vwap线以上下跌的分钟线对应的成交额
        above_vwap_amt = amt_min.where((open_adj_min.values > vwap_adj.values) & (close_adj_min.values < open_adj_min.values)).sum() 
        # 计算今日五日vwap线以下上涨的分钟线对应的成交额
        below_vwap_amt = amt_min.where((open_adj_min.values < vwap_adj.values) & (close_adj_min.values > open_adj_min.values)).sum()
        return (below_vwap_amt - above_vwap_amt) / amt.iloc[-1]

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result
