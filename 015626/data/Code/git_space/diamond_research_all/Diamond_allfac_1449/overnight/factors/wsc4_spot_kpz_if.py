import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc4_spot_kpz_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # dpo技术指标
        close_000905 = data_dict['close_000905.SH']
        close_000905 = close_000905.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        N = 20
        dpo = close_000905 - ts_delay(ts_mean(close_000905, N), int(N/2+1))
        factor_raw = abs(dpo - ts_median(dpo, 60))
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor