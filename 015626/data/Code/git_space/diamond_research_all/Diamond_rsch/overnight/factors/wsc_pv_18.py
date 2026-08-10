from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_18(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'amount_000905.SH', 'open_000905.SH', 'high_000905.SH', 'low_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # wvad技术指标_短参数，用分钟内的价格变化给成交额加权，变化越大则权重越低，但是注意后面加了负号
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        open_spot = data_dict['open_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        high_spot = data_dict['high_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot = data_dict['low_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        amount_spot = data_dict['amount_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 41
        wvad = ts_sum((close_spot - open_spot) / (high_spot - low_spot) * amount_spot, n)
        wvad = get_single_minute_data(wvad, trade_stop_time)
        factor = -wvad.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



