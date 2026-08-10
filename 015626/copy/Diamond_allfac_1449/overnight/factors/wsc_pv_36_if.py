from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_36_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000300.SH', 'low_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 过去230分钟沪深300指数每分钟high/low的最大值，值越大因子值越大，波动类因子
        high_spot_if = data_dict['high_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot_if = data_dict['low_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        n = 230
        hl_max = ts_max(high_spot_if / low_spot_if, n)
        factor_raw = get_single_minute_data(hl_max, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor


