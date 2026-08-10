from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_16(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'amount_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # obv技术指标
        close_spot = data_dict['close_000905.SH']
        amount_spot = data_dict['amount_000905.SH']

        n = 60
        vol = amount_spot.copy()
        vol[ts_delta(close_spot, 1) == 0] = 0
        vol[ts_delta(close_spot, 1) < 0] = -amount_spot
        obv = ts_sum(vol, n)
        obv = get_single_minute_data(obv, trade_stop_time)
        factor = -obv.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor