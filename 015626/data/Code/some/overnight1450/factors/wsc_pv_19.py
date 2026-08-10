from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_19(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # pvt技术指标
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        volume_spot = data_dict['volume_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n1 = 110
        n2 = 500
        pvt = ts_pct_change(close_spot, 1) * volume_spot
        pvt_ma1 = ts_mean(pvt, n1)
        pvt_ma2 = ts_mean(pvt, n2)
        factor_raw = pvt_ma1 - pvt_ma2
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



