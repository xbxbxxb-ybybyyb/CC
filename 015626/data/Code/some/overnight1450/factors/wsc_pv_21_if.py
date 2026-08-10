from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_21_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH', 'high_000300.SH', 'low_000300.SH', 'volume_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 20分钟vwap和close之差，类似于结算指标
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        high_spot_if = data_dict['high_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot_if = data_dict['low_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        volume_spot_if = data_dict['volume_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 20
        typical = (high_spot_if + low_spot_if + close_spot_if) / 3
        mf = volume_spot_if * typical
        volume_sum = ts_sum(volume_spot_if, n)
        mf_sum = ts_sum(mf, n)
        vwap = mf_sum / volume_sum
        factor_raw = vwap - close_spot_if
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



