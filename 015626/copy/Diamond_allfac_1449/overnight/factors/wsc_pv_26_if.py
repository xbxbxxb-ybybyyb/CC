from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_26_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 下行波动率/上行波动率，下跌的时间越多，则下行波动率越大（见代码部分下行波动率的计算方法），反转类因子
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n1 = 10
        n2 = 20
        close_std = ts_std(close_spot_if, n1)
        ustd = close_std.copy()
        ustd[ts_delta(close_spot_if, 1)<=0] = 0
        ustd = ts_sum(ustd, n2)
        dstd = close_std.copy()
        dstd[ts_delta(close_spot_if, 1)>=0] = 0
        dstd = ts_sum(dstd, n2)
        rvi = dstd / (ustd + dstd)
        factor_raw = get_single_minute_data(rvi, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



