from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_39_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000300.SH', 'open_000300.SH', 'low_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # ar技术指标，对沪深300指数，low与open之差相比high与open之差越大，因子值越大，有点类似下影线形态的指标
        high_spot_if = data_dict['high_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        open_spot_if = data_dict['open_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot_if = data_dict['low_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        n = 50
        ar = ts_sum(high_spot_if - open_spot_if, n) / ts_sum(open_spot_if - low_spot_if, n)
        factor_raw = get_single_minute_data(ar, trade_stop_time)
        factor = -factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor

