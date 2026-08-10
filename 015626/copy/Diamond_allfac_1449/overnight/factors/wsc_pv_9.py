import scipy.stats
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import warnings
from overnight.utility import *


class wsc_pv_9(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_000300.SH', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300_日alla_Univ分位数'''
        close_000300 = data_dict['close_000300.SH']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        preclose_alla_daily = data_dict['preclose_alla_daily']

        close_000300_daily_1449 = close_000300.iloc[close_000300.index.indexer_at_time(trade_stop_time)]
        close_000300_daily_1500 = close_000300.iloc[close_000300.index.indexer_at_time('15:00')]
        close_000300_daily_1449.index = pd.to_datetime(close_000300_daily_1449.index.date)
        close_000300_daily_1500.index = pd.to_datetime(close_000300_daily_1500.index.date)
        close_000300_daily_1500 = close_000300_daily_1500.reindex(close_000300_daily_1449.index)
        spot_ret = close_000300_daily_1449 / close_000300_daily_1500.shift(1) - 1
        spot_ret.index.name = 'dt'
        stk_ret = close_alla_daily_1449 / preclose_alla_daily - 1

        i_date = stk_ret.index[-1]
        factor = pd.DataFrame(index=[i_date], columns=[self.__class__.__name__])
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            factor.loc[i_date] = scipy.stats.percentileofscore(stk_ret.loc[i_date].dropna(), spot_ret.loc[i_date])
        return factor
