import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_factor_settlement(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE', 'recent_month_mask', 'amount_IC.CFE', 'volume_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 股指期货结算价/收盘价，＞0.15%置为1，其余为0，反应了期指尾盘下跌情况。
        future_close = data_dict['close_IC.CFE']
        future_mask = data_dict['recent_month_mask']
        future_amount = data_dict['amount_IC.CFE']
        future_volume = data_dict['volume_IC.CFE']
        
        amount_sum = ts_sum(future_amount, 60)
        volume_sum = ts_sum(future_volume, 60)
        vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
        vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].to_frame()
        vwap_60.index = pd.to_datetime(vwap_60.index.date)
        vwap_60.index.name = 'dt'

        close_stop_time = future_close[future_mask].sum(axis=1)
        close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].to_frame()
        close_stop_time.index = pd.to_datetime(close_stop_time.index.date)
        close_stop_time.index.name = 'dt'

        factor = replace_zero((vwap_60/200) / close_stop_time)
        factor[factor<1.0015] = 0
        factor[factor>0] = 1


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor