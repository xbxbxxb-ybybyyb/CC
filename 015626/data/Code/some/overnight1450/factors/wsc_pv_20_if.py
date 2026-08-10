from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_20_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=50, **kwargs)

    def on_bar(self, data_dict):
        # 尾盘收益率的反转指标
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 50
        nvi_inc = ts_pct_change(close_spot_if, 1)
        nvi = ts_sum(nvi_inc, n)
        nvi = get_single_minute_data(nvi, trade_stop_time)
        factor = -nvi.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



