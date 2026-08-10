from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_15(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'close_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票，第二天开盘涨停的股票比例减去尾盘涨停的股票比例
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily_1449 == limit_alla_daily)  # 判断截止到1449，股票是否涨停
        limit_judgement3 = (open_alla_daily_0930 == limit_alla_daily)  # 判断当天0930，股票是否涨停
        limit_judgement4 = limit_judgement1.shift(1) * limit_judgement2  # 前一天涨停的股票今天尾盘是否继续涨停
        limit_judgement5 = limit_judgement1.shift(1) * limit_judgement3  # 前一天涨停的股票今天早盘是否继续涨停

        
        factor = (limit_judgement5.sum(axis=1) - limit_judgement4.sum(axis=1)) / close_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor

    