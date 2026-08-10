from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_14(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH', 'low_000905.SH', 'close_000905.SH', 'volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # vao技术指标
        volume_spot = data_dict['volume_000905.SH']
        close_spot = data_dict['close_000905.SH']
        high_spot = data_dict['high_000905.SH']
        low_spot = data_dict['low_000905.SH']

        weighted_volume = volume_spot * (close_spot - (high_spot + low_spot) / 2)
        vao = ts_mean(weighted_volume, 60)
        vao = get_single_minute_data(vao, trade_stop_time)
        factor = -vao.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor