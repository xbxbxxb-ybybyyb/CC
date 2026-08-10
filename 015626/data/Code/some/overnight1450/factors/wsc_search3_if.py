import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_search3_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 算法搜索
        high_000905 = data_dict['high_000905.SH'].to_frame()

        factor_raw = ts_std(high_000905, 75)
        factor = ts_rank(factor_raw, 1200)
        factor = get_single_minute_data(factor, trade_stop_time)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor