from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_30_icif(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 中证500和沪深300的5分钟收益率在过去120分钟的相关性，相关性越大，因子值越大
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        spot_ret_ic = ts_pct_change(close_spot, 5)
        spot_ret_if = ts_pct_change(close_spot_if, 5)
        factor_raw = ts_corr(spot_ret_ic, spot_ret_if, 120)
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor



