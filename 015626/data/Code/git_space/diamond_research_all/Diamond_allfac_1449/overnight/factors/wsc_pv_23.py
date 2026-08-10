from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_23(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['amount_000905.SH', 'close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # rsiv技术指标，中证500指数上涨分钟的成交额比上总成交额，比值越大因子值越小，反转因子，在IF合约上表现更好
        amount_spot = data_dict['amount_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 550
        volup = amount_spot.copy()
        volup[ts_delta(close_spot, 1) <= 0] = 0
        voldown = amount_spot.copy()
        voldown[ts_delta(close_spot, 1) >= 0] = 0
        sumup = ts_sum(volup, n)
        sumdown = ts_sum(voldown, n)
        rsiv = 100 * sumup / (sumup + sumdown)
        rsiv = get_single_minute_data(rsiv, trade_stop_time)
        factor = -rsiv.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



