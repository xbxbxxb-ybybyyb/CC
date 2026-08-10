import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc10_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 近远月价差的日内变化
        future_close = data_dict['close_IC.CFE']

        recent_month_close = future_close.stack().groupby('dt').first()  # 获取近月合约的close序列
        far_month_close = future_close.stack().groupby('dt').nth(1)  # 获取次近月合约的close序列
        price_spread = recent_month_close - far_month_close
        price_spread_1449 = price_spread.iloc[price_spread.index.indexer_at_time(trade_stop_time)]
        price_spread_1449.index = pd.to_datetime(price_spread_1449.index.date)
        price_spread_0930 = price_spread.iloc[price_spread.index.indexer_at_time(futures_data_morning_begin)]
        price_spread_0930.index = pd.to_datetime(price_spread_0930.index.date)

        factor = (price_spread_0930 - price_spread_1449).to_frame()
        factor.index.name = 'dt'
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor