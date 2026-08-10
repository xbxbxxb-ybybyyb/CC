from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_27_ih(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000016.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # RSI技术指标，计算上涨时刻价格位移和全部时刻价格总位移之比，反转因子
        close_spot_ih = data_dict['close_000016.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 25
        close_up = ts_delta(close_spot_ih, 1)
        close_up[close_up<=0] = 0
        close_down = abs(ts_delta(close_spot_ih, 1))
        close_down[close_up>0] = 0
        close_up_ma = ts_mean(close_up, n)
        close_down_ma = ts_mean(close_down, n)
        rsi = 100 * close_up_ma / (close_up_ma + close_down_ma)
        factor_raw = get_single_minute_data(rsi, trade_stop_time)
        factor = -factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



