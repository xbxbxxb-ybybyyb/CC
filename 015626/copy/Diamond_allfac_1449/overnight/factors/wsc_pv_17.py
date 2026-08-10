from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_17(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'amount_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=100, **kwargs)

    def on_bar(self, data_dict):
        # vr技术指标
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        amount_spot = data_dict['amount_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 450
        av = amount_spot.copy()
        bv = amount_spot.copy()
        cv = amount_spot.copy()
        spot_delta = ts_delta(close_spot, 1)
        av[spot_delta < 0] = 0
        bv[spot_delta > 0] = 0
        cv[spot_delta == 0] = 0
        avs = ts_sum(av, n)
        bvs = ts_sum(bv, n)
        cvs = ts_sum(cv, n)
        vr = (avs + cvs / 2) / (bvs + cvs / 2)
        vr = get_single_minute_data(vr, trade_stop_time)
        factor = -vr.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



