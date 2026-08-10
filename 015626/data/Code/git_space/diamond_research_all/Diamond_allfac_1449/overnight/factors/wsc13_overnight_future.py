import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc13_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 近月合约和次近月合约尾盘收益率之差
        future_close = data_dict['close_IC.CFE']

        future_ret = ts_pct_change(future_close.stack().groupby('dt').nth(1), 30)
        future_ret = future_ret.iloc[future_ret.index.indexer_at_time(trade_stop_time)]
        future_ret.index = pd.to_datetime(future_ret.index.date)

        future_ret1 = ts_pct_change(future_close.stack().groupby('dt').nth(0), 30)
        future_ret1 = future_ret1.iloc[future_ret1.index.indexer_at_time(trade_stop_time)]
        future_ret1.index = pd.to_datetime(future_ret1.index.date)

        factor = (future_ret - future_ret1).to_frame()
        factor.index.name = 'dt'
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor