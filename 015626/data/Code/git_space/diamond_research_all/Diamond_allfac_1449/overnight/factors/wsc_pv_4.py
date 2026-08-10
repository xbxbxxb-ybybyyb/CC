from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_4(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_000300.SH_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300过去20天波动率'''

        close_000300_daily_trun = data_dict['close_000300.SH_daily_' + minute_to_daily_tag]
        
        index_ret = ts_pct_change(close_000300_daily_trun, 1)
        factor = ts_std(index_ret, 20)     
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor