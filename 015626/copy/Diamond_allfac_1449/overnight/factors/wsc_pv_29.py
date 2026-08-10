import datetime as dt
from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_29(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # factor_raw近似于隔夜收益率，因此该因子近似于隔夜收益率的反转效应
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        spot_close_mean = ts_mean(close_spot, 10)
        spot_ret = ts_pct_change(spot_close_mean, 10)
        factor_raw = get_single_minute_data(spot_ret, dt.time(futures_data_morning_begin.hour, futures_data_morning_begin.minute+5))
        factor = -factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



