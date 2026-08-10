from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_21(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停且今天尾盘继续涨停的股票比例减去前一个交易日跌停且今天尾盘继续跌停的股票比例
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(stopping_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement3 = (close_alla_daily_trun == limit_alla_daily)  # 判断当天尾盘股票是否涨停
        limit_judgement4 = (close_alla_daily_trun == stopping_alla_daily)  # 判断当天尾盘股票是否跌停
        limit_judgement5 = limit_judgement1.shift(1) * limit_judgement3  # 前一个交易日涨停的股票今天尾盘是否涨停
        limit_judgement6 = limit_judgement2.shift(1) * limit_judgement4  # 前一个交易日跌停的股票今天尾盘是否跌停
        
        
        factor = (limit_judgement6.sum(axis=1) - limit_judgement5.sum(axis=1)) / close_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor