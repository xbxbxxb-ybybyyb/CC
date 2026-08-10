from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc42_overnight_index_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 中证500当天收益率绝对值是否＞1.5%
        index_close_ic = data_dict['close_000905.SH']
        
        index_close_ic_1449 = get_single_minute_data(index_close_ic, trade_stop_time)
        index_ret_ic_1449 = ts_pct_change(index_close_ic_1449, 1)
        index_ret_ic_1449[abs(index_ret_ic_1449)>0.015] = 0.875
        index_ret_ic_1449[index_ret_ic_1449<0.875] = 0
        factor = index_ret_ic_1449.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor