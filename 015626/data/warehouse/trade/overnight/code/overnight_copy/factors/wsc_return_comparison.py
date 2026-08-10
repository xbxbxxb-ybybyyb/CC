import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_return_comparison(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 比较hs300指数和zz500指数过去三分钟收益率大小
        close_000905 = data_dict['close_000905.SH']
        close_000300 = data_dict['close_000300.SH']
        close_000300 = close_000300.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close_000905 = close_000905.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        ret_000905 = ts_pct_change(close_000905, 3)
        ret_000300 = ts_pct_change(close_000300, 3)
        ret_diff = ret_000905 - ret_000300
        ret_diff[ret_diff > 0] = 1
        ret_diff[ret_diff <= 0] = 0
        temp = ts_sum(ret_diff, 180)
        factor_raw = ts_sum(ret_diff, 30) / replace_zero(temp)
        factor_mean = ts_mean(factor_raw, 10).to_frame()
        factor = ts_rank(factor_mean, 1200)
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor