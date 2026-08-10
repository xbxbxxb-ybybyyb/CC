from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_25(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['amount_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # macdvol技术指标，尾盘20分钟的平均成交额相比尾盘40分钟缩量，则倾向于开仓
        amount_spot = data_dict['amount_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n1 = 20
        n2 = 40
        n3 = 10
        macdvol = ts_mean(amount_spot, n1) - ts_mean(amount_spot, n2)
        sig = ts_mean(macdvol, n3)
        factor_raw = get_single_minute_data(sig, trade_stop_time)
        factor = -factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



