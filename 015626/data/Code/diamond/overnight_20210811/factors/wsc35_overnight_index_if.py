import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class wsc35_overnight_index_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH_daily_' + minute_to_daily_tag]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # pos技术指标，反转因子
        index_close_daily = data_dict['close_000300.SH_daily_' + minute_to_daily_tag]

        n = 75
        price1 = ts_delta(index_close_daily, n) / ts_delay(index_close_daily, n)
        pos1 = (price1 - ts_min(price1, n)) / (ts_max(price1, n) - ts_min(price1, n))
        factor = -pos1.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        
        return factor