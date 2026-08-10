from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_15(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH', 'low_000905.SH', 'close_000905.SH', 'volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=80, **kwargs)

    def on_bar(self, data_dict):
        # mfi技术指标
        close_spot = data_dict['close_000905.SH']
        high_spot = data_dict['high_000905.SH']
        low_spot = data_dict['low_000905.SH']
        volume_spot = data_dict['volume_000905.SH']

        n = 300
        typical_price = (high_spot + low_spot + close_spot) / 3
        mf = typical_price * volume_spot
        mf_pos = mf.copy()
        mf_pos[ts_delta(typical_price, 1) < 0] = 0
        mf_neg = mf.copy()
        mf_neg[ts_delta(typical_price, 1) > 0] = 0
        mf_pos = ts_sum(mf_pos, n)
        mf_neg = ts_sum(mf_neg, n)
        mfi = 100 - 100 / (1 + mf_pos / mf_neg)
        mfi = get_single_minute_data(mfi, trade_stop_time)
        factor = -mfi.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor