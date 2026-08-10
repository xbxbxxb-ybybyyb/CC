import pandas as pd
from overnight.factor_generator import FactorGenerator
from operators_wsc import *



class wsc_hf3(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        super().__init__(*args, required_columns=['Ask1AmtMean_500'], ts_norm_bars=0, **kwargs)

    def on_bar(self, data):
        # factor logic: 见每一行后面的注释
        a = data['Ask1AmtMean_500'].sum(axis=1) # 当下分钟成分股的卖一价总挂单额
        factor_raw = ts_rank(a, 30) # 表示当下挂单额在过去30分钟的排序
        factor_mean = ts_mean(factor_raw, 45)
        factor = -ts_rank(factor_mean, 1200)
        factor = factor.to_frame()
        
        factor = factor.iloc[factor.index.indexer_at_time('14:49:00')]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = 0
        return factor