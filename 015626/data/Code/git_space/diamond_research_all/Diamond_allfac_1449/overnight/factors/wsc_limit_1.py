from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_1(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日开盘涨停的股票比例
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']

        limit_judgement1 = (open_alla_daily_trun == limit_alla_daily)  # 判断股票早盘是否涨停
        
        factor = -limit_judgement1.sum(axis=1) / open_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor