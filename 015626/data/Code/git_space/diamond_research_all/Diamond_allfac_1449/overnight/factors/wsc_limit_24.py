import pandas as pd
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_24(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'close_alla_daily', 'limit_alla_daily', 'close_000906.SH', 'open_000906.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均超额收益（不包含隔夜收益）
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_000906 = data_dict['close_000906.SH']
        open_000906 = data_dict['open_000906.SH']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        open_000906_0930 = open_000906.iloc[open_000906.index.indexer_at_time(futures_data_morning_begin)]
        open_000906_0930.index = pd.to_datetime(open_000906_0930.index.date)
        close_000906_1449 = close_000906.iloc[close_000906.index.indexer_at_time(trade_stop_time)]
        close_000906_1449.index = pd.to_datetime(close_000906_1449.index.date)
        index_ret = close_000906_1449 / open_000906_0930 - 1
        index_ret.index.name = 'dt'


        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_1449 / open_alla_daily_0930 - 1


        factor = (limit_judgement1.shift(1) * stk_ret).mean(axis=1) - index_ret
        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor