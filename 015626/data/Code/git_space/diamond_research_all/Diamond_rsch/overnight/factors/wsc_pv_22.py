from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_22(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)


    def on_bar(self, data_dict):
        # rocvol技术指标，在IF合约上效果更好，计算成交量的动量
        volume_spot = data_dict['volume_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 60
        rocvol = ts_pct_change(volume_spot, n)
        rocvol = get_single_minute_data(rocvol, trade_stop_time)
        factor = -rocvol.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



