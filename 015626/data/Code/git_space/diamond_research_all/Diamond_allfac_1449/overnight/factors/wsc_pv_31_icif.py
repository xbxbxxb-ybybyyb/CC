import pandas as pd
from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator



class wsc_pv_31_icif(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 中证500和沪深300的1分钟收益率之差的日内波动率，波动率越大，因子值越大，和pv_30的逻辑是反过来的，相关性也近乎为0，但是效果都很好
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 1
        spot_ret_ic = ts_pct_change(close_spot, n)
        spot_ret_if = ts_pct_change(close_spot_if, n)
        spot_ret_diff = (spot_ret_ic - spot_ret_if).between_time(futures_data_morning_begin, trade_stop_time)
        factor_raw = spot_ret_diff.groupby(spot_ret_diff.index.date).std()
        factor_raw.index = pd.to_datetime(factor_raw.index)
        factor_raw.index.name = 'dt'
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor


