import pandas as pd
from overnight.factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc7_overnight_hf(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        super().__init__(*args, required_columns=['BidAskSpreadMean_500', 'close_500', 'weight_500'],
                                                 ts_norm_bars=20, **kwargs)

    def on_bar(self, hf_data):
        # 尾盘时的个股bid_ask_spread/close的加权平均值，值越大说明买卖价差越大，出于流动性溢价，此时买入第二天会跳涨以弥补承担的流动性风险
        close_500 = hf_data['close_500']
        weight_500 = hf_data['weight_500']
        BidAskSpreadMean_500 = hf_data['BidAskSpreadMean_500']

        temp = close_500.copy()
        temp = replace_zero(temp)
        a_daily = (BidAskSpreadMean_500 / temp * weight_500).sum(axis=1)
        a_daily = ts_mean(a_daily, 1)
        a_daily = a_daily.iloc[a_daily.index.indexer_at_time('14:49:00')].to_frame()
        a_daily.index = pd.to_datetime(a_daily.index.date)
        a_daily.index.name = 'dt'
        # factor = ts_rank(a_daily, 20)
        # factor[factor<=0] = np.nan
        factor = a_daily

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor