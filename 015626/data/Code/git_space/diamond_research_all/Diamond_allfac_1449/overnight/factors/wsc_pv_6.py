from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_6(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_000300.SH_daily_' + minute_to_daily_tag
        name2 = 'close_000905.SH_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300与中证500日收益率之差'''
        close_000300_daily_trun = data_dict['close_000300.SH_daily_' + minute_to_daily_tag]
        close_000905_daily_trun = data_dict['close_000905.SH_daily_' + minute_to_daily_tag]
        
        spot_ret_if = ts_pct_change(close_000300_daily_trun, 1)
        spot_ret_ic = ts_pct_change(close_000905_daily_trun, 1)
        factor = spot_ret_if - spot_ret_ic
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor