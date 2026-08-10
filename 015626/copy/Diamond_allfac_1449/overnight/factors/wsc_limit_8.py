from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_8(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'limit_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=35, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日开盘股票涨停比例减去跌停比例
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (open_alla_daily_trun == limit_alla_daily)  # 判断开盘时股票是否涨停
        limit_judgement2 = (open_alla_daily_trun == stopping_alla_daily)  # 判断开盘时股票是否跌停
        
        
        factor = (limit_judgement2.sum(axis=1) - limit_judgement1.sum(axis=1)) / open_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor